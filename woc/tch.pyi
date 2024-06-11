from typing import Iterator

class TCHashDB:
    """Object representing a TokyoCabinet Hash table"""

    def __init__(self, path: str, ro: bool = False) -> None:
        """
        Create a new TokyoCabinet hash table object.

        :param path: path to the database file
        :param ro: if True, open in lock-free read-only mode; if False, lock and open in write mode (create if not exists)
        :raises OSError: if the database cannot be opened
        """
        ...

    def __iter__(self) -> "Iterator[bytes]": ...
    def get(self, key: bytes) -> bytes:
        """
        Get a record.

        :raises KeyError: if the key is not found
        :raises OSError: if the operation fails
        """
        ...

    def put(self, key: bytes, value: bytes) -> None:
        """
        Upsert a record.

        :raises OSError: if the operation fails
        """
        ...

    def delete(self, key: bytes) -> None:
        """
        Delete a record from the database.

        :raises OSError: if the operation fails
        """
        ...

    def drop(self) -> None:
        """
        Delete all records in the database.

        :raises OSError: if the operation fails
        """
        ...

    def close(self) -> None:
        """
        Close the database.

        :raises OSError: if the operation fails
        """
        ...

    def __getitem__(self, key: bytes) -> bytes: ...
    def __setitem__(self, key: bytes, value: bytes) -> None: ...
    def __delitem__(self, key: bytes) -> None: ...
    def __len__(self) -> int: ...
    def __del__(self) -> None: ...
