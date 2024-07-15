import logging
import os
from tqdm import tqdm

from woc.base import WocFile
from woc.local import WocMapsLocal
from woc.utils import sample_md5


def check_file(fobj: WocFile):
    assert fobj.size == os.path.getsize(
        fobj.path
    ), f"Size mismatch for {fobj.path}: {os.path.getsize(fobj.path)} != {fobj.size}"

    if not fobj.digest:
        return

    _digest = sample_md5(fobj.path)
    assert (
        _digest == fobj.digest
    ), f"Digest mismatch for {fobj.path}: {_digest} != {fobj.digest}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Checks integrity of WoC files")
    parser.add_argument(
        "-p", "--profile", type=str, help="The path to the profile file", default=None
    )
    args = parser.parse_args()

    woc = WocMapsLocal(args.profile)
    errs = []
    files_to_check = []
    for obj in woc.objects:
        files_to_check.extend(obj.shards)
    for obj in woc.maps:
        files_to_check.extend(obj.larges.values())
        files_to_check.extend(obj.shards)
    files_to_check = list(filter(lambda x: x, files_to_check))

    for fobj in tqdm(files_to_check, desc="Checking files"):
        try:
            check_file(fobj)
        except AssertionError as e:
            logging.error(e)
            errs.append(fobj.path)

    if errs:
        logging.error(f"Errors found in the following files: {errs}")
        raise AssertionError("Errors found in some files")
