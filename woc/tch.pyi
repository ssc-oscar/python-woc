from typing import Iterator

class TCHashDB:
    """Object representing a TokyoCabinet Hash table"""

    def __init__(self, path: bytes, ro: bool = False) -> None:
        """
        Create a new TokyoCabinet hash table object.
        :path: *encoded* path to the database file
        :ro: if True, open in lock-free read-only mode; if False, lock and open in write mode (create if not exists)
        """
        ...

    def __iter__(self) -> 'Iterator[bytes]':
        ...

    def get(self, key: bytes) -> bytes:
        """Get a record, raise KeyError if not found"""
        ...

    def put(self, key: bytes, value: bytes) -> None:
        """Upsert a record"""
        ...

    def delete(self, key: bytes) -> None:
        """Delete a record from the database"""
        ...

    def drop(self) -> None:
        """Delete all records in the database"""
        ...

    def close(self) -> None:
        """Close the database"""
        ...

    def __getitem__(self, key: bytes) -> bytes:
        ...

    def __setitem__(self, key: bytes, value: bytes) -> None:
        ...

    def __delitem__(self, key: bytes) -> None:
        ...

    def __len__(self) -> int:
        ...

    def __del__(self) -> None:
        ...