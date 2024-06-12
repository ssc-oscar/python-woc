# cython: language_level=3str, wraparound=False, boundscheck=False, nonecheck=False, profile=True, linetrace=True

from libc.stdint cimport uint32_t, uint8_t

# Make utility functions accessible from Python -> easier testing
cpdef uint32_t fnvhash(bytes data)
cpdef unber(bytes buf)
cpdef (int, int) lzf_length(bytes raw_data)
cpdef get_tch(str path)
cpdef uint8_t get_shard(bytes key, uint8_t sharding_bits, bint use_fnv_keys)
# cpdef bytes get_from_tch(bytes key, list shards, int sharding_bits, bint use_fnv_keys)