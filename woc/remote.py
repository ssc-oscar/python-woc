import asyncio
import logging
import os
import threading
from datetime import datetime, timedelta
from functools import cached_property
from json import JSONDecodeError
from typing import (
    AsyncGenerator,
    Awaitable,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
    Union,
)
from urllib.parse import quote_plus

import httpx
from tqdm.asyncio import tqdm_asyncio

from .base import WocMap, WocMapsBase, WocObject


class RateLimitHandler:
    def __init__(self):
        self.next_request_time = datetime.now()
        self.lock = asyncio.Lock()

    async def wait_if_needed(self):
        async with self.lock:
            now = datetime.now()
            if now < self.next_request_time:
                wait_time = (self.next_request_time - now).total_seconds()
                await asyncio.sleep(wait_time)

    def update_next_request_time(self, retry_after: int):
        self.next_request_time = datetime.now() + timedelta(seconds=retry_after)


async def fetch_with_rate_limit(
    url: str,
    client: httpx.AsyncClient,
    rate_limiter: RateLimitHandler,
    max_retries: int = 4,
    base_delay: int = 4,
) -> Optional[httpx.Response]:
    for attempt in range(max_retries):
        await rate_limiter.wait_if_needed()

        response = await client.get(url)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            rate_limiter.update_next_request_time(retry_after)

            if attempt < max_retries - 1:
                delay = base_delay * (2**attempt)  # exponential backoff
                logging.warning(
                    f"Rate limit hit for {url}. "
                    f"Waiting {retry_after} seconds. Attempt {attempt + 1}/{max_retries}"
                )
                await asyncio.sleep(delay)
                continue

        if response.status_code in (404, 400):
            try:
                _msg = response.json()["detail"]
            except (KeyError, JSONDecodeError):
                _msg = response.text
            raise KeyError(_msg)

        response.raise_for_status()
        return response.json()


class WocMapsRemoteAsync(WocMapsBase):
    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        max_connections: Optional[int] = 10,
        version: Optional[Union[str, List[str]]] = None,
    ):
        self.base_url = (
            base_url or os.getenv("WOC_BASE_URL") or "https://worldofcode.org/api"
        )
        self.api_key = api_key or os.getenv("WOC_API_KEY")
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else None,
            base_url=self.base_url,
            limits=httpx.Limits(
                max_connections=max_connections if max_connections else 10
            ),
        )
        self.rate_limiter = RateLimitHandler()
        if version is not None:
            raise NotImplementedError(
                "Versioning is not implemented in WoC HTTP API. "
                "If you feel it is necessary, please create a feature request at "
                "https://github.com/ssc-oscar/python-woc/issues/new"
            )

    async def get_maps(self) -> List[WocMap]:
        r = await fetch_with_rate_limit(
            "/lookup/map",
            self.client,
            self.rate_limiter,
        )
        return [
            WocMap(
                name=m["name"],
                version=m["version"],
                sharding_bits=m["sharding_bits"],
                shards=[],
                larges={},
                dtypes=m["dtypes"],
            )
            for m in r["data"]
        ]

    @property
    def maps(self):
        raise NotImplementedError("use await get_maps() instead")

    async def get_objects(self) -> List[WocObject]:
        r = await fetch_with_rate_limit(
            "/lookup/object",
            self.client,
            self.rate_limiter,
        )
        return [
            WocObject(
                name=o["name"],
                sharding_bits=o["sharding_bits"],
                shards=[],
            )
            for o in r["data"]
        ]

    @property
    def objects(self):
        raise NotImplementedError("use await get_objects() instead")

    async def get_values(
        self, map_name: str, key: Union[bytes, str]
    ) -> Union[List[str], Tuple[str], List[Tuple[str]]]:
        r = await fetch_with_rate_limit(
            f"/lookup/map/{map_name}/{key}",
            self.client,
            self.rate_limiter,
        )
        return r["data"]

    async def _get_many(
        self,
        url_prefix: str,
        keys: List[Union[bytes, str]],
        progress: bool = False,
    ):
        # first we need to split the keys into chunks of 10
        chunks = [keys[i : i + 10] for i in range(0, len(keys), 10)]
        result = {}
        errors = {}
        promises = [
            fetch_with_rate_limit(
                f"{url_prefix}?{'&'.join([f'q={quote_plus(k)}' for k in chunk])}",
                self.client,
                self.rate_limiter,
            )
            for chunk in chunks
        ]
        # fire all requests in parallel
        if progress:
            responses = await tqdm_asyncio.gather(*promises)
        else:
            responses = await asyncio.gather(*promises)
        for response in responses:
            result.update(response["data"])
            if "errors" in response:
                errors.update(response["errors"])
        return result, errors

    async def get_values_many(
        self, map_name: str, keys: List[Union[bytes, str]], progress: bool = False
    ) -> Tuple[Dict[str, Union[List[str], Tuple[str], List[Tuple[str]]]], Dict[str, str]]:
        """
        Eqivalent to getValues in WoC Perl API but fetch multiple keys at once.

        Similar to get_values, this function uses WoC batch API to fetch multiple keys at once.
        It returns a tuple of two dictionaries: [results, errors].
        """
        return await self._get_many(f"/lookup/map/{map_name}", keys, progress)

    async def iter_values(
        self, map_name: str, key: Union[bytes, str]
    ) -> AsyncGenerator[List[str], None]:
        cursor = 0
        while cursor is not None:
            r = await fetch_with_rate_limit(
                f"/lookup/map/{map_name}/{key}?cursor={cursor}",
                self.client,
                self.rate_limiter,
            )
            cursor = r["nextCursor"] if "nextCursor" in r else None
            yield r["data"]

    async def show_content(
        self, obj_name: str, key: Union[bytes, str]
    ) -> Union[
        List[Tuple[str, str, str]],
        str,
        Tuple[str, Tuple[str, str, str], Tuple[str, str, str], str],
    ]:
        r = await fetch_with_rate_limit(
            f"/lookup/object/{obj_name}/{key}",
            self.client,
            self.rate_limiter,
        )
        return r["data"]

    async def show_content_many(
        self, obj_name: str, keys: List[Union[bytes, str]], progress: bool = False
    ) -> Tuple[
        Dict[
            str,
            Union[
                List[Tuple[str, str, str]],
                str,
                Tuple[str, Tuple[str, str, str], Tuple[str, str, str], str],
            ],
        ],
        Dict[str, str],
    ]:
        """
        Eqivalent to showCnt in WoC Perl API but fetch multiple keys at once.

        Similar to show_content, this function uses WoC batch API to fetch multiple keys at once.
        It returns a tuple of two dictionaries: [results, errors].
        """
        return await self._get_many(f"/lookup/object/{obj_name}", keys, progress)

    async def count(self, map_name: str) -> int:
        if "map_name" in ("blob", "commit", "tag", "tree"):
            r = await fetch_with_rate_limit(
                f"/lookup/object/{map_name}/count",
                self.client,
                self.rate_limiter,
            )
            return r["data"]
        else:
            r = await fetch_with_rate_limit(
                f"/lookup/map/{map_name}/count",
                self.client,
                self.rate_limiter,
            )
            return r["data"]

    async def all_keys(self, map_name: str) -> Generator[bytes, None, None]:
        raise NotImplementedError(
            "all_keys is not implemented in WoC HTTP API. "
            "If you feel it is necessary, please create a feature request at "
            "https://github.com/ssc-oscar/python-woc/issues/new"
        )


def _start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()


class WocMapsRemote(WocMapsRemoteAsync):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # run the event loop on a background thread
        # so it works in jupyter notebook
        # ref: https://stackoverflow.com/questions/52232177/runtimeerror-timeout-context-manager-should-be-used-inside-a-task/69514930#69514930
        self._loop = asyncio.new_event_loop()
        _t = threading.Thread(
            target=_start_background_loop, args=(self._loop,), daemon=True
        )
        _t.start()

    def _asyncio_run(self, coro: Awaitable, timeout=30):
        """
        Runs the coroutine in an event loop running on a background thread, and blocks the current thread until it returns a result. This plays well with gevent, since it can yield on the Future result call.

        :param coro: A coroutine, typically an async method
        :param timeout: How many seconds we should wait for a result before raising an error
        """
        return asyncio.run_coroutine_threadsafe(coro, self._loop).result(timeout=timeout)

    def _asyncio_gather(self, *futures, return_exceptions=False) -> list:
        """
        A version of asyncio.gather that runs on the internal event loop
        """

        async def gather():
            return await asyncio.gather(*futures, return_exceptions=return_exceptions)

        return asyncio.run_coroutine_threadsafe(gather(), loop=self._loop).result()

    def get_values(self, map_name: str, key: str) -> List[str]:
        return self._asyncio_run(super().get_values(map_name, key))

    def get_values_many(
        self, map_name: str, keys: List[str], progress: bool = False
    ) -> Tuple[Dict[str, List[str]], Dict[str, str]]:
        return self._asyncio_run(super().get_values_many(map_name, keys, progress))

    def iter_values(self, map_name: str, key: str) -> Generator[List[str], None, None]:
        async_gen = super().iter_values(map_name, key)
        while True:
            try:
                for i in self._asyncio_run(async_gen.__anext__()):
                    yield i
            except StopAsyncIteration:
                break

    def show_content(self, obj_name: str, key: str) -> List[Tuple[str, str, str]]:
        return self._asyncio_run(super().show_content(obj_name, key))

    def show_content_many(
        self, obj_name: str, keys: List[str], progress: bool = False
    ) -> Tuple[Dict[str, List[Tuple[str, str, str]]], Dict[str, str]]:
        return self._asyncio_run(super().show_content_many(obj_name, keys, progress))

    def count(self, map_name: str) -> int:
        return self._asyncio_run(super().count(map_name))

    def all_keys(self, map_name: str) -> Generator[bytes, None, None]:
        return self._asyncio_run(super().all_keys(map_name))

    @cached_property
    def maps(self) -> List[WocMap]:
        return self._asyncio_run(super().get_maps())

    @cached_property
    def objects(self) -> List[WocObject]:
        return self._asyncio_run(super().get_objects())
