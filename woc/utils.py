import hashlib
import os


def sample_md5(file_path: str, skip=0, size=None) -> str:
    """
    Divide the file into chunks and calculate the MD5 digest of the first 128 bytes of each chunk.

    :param file_path: The path to the file.
    :param skip: The number of bytes to skip from the beginning of the file. Defaults to 0.
    :param size: The number of bytes to for hashing. If None, the entire file (minus the skip) is considered.
    :return: A tuple containing the size of the considered portion and the 16-character MD5 digest.
    """

    fsize = os.path.getsize(file_path)

    if size is None:
        size = fsize - skip
    assert (
        skip + size <= fsize
    ), f"supplied size {size}B > file size {os.path.getsize(file_path)}B"

    dig = hashlib.md5()

    # hash all bytes if file is small
    if size <= 4096:  # typical block size of ext4
        with open(file_path, "rb") as f:
            f.seek(skip)
            dig.update(f.read(size))
            return size, dig.hexdigest()[:16]

    # A heuristic to find the optimal chunk size
    # Number of chunks is between 2 and 8, chunk size must be a power of 2
    chunk_size = 2 ** ((size // size.bit_length()).bit_length() + 2)
    num_chunks = (size - 256) // chunk_size  # don't hash the same bytes twice

    with open(file_path, "rb") as f:
        f.seek(skip)
        dig.update(f.read(128))
        for _ in range(num_chunks):
            f.seek(chunk_size - 128, os.SEEK_CUR)
            dig.update(f.read(128))
        f.seek(skip + size - 128)
        dig.update(f.read(128))

    return dig.hexdigest()[:16]
