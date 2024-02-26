# cython: language_level=3str, wraparound=False, boundscheck=False, nonecheck=False

from libc.stdint cimport uint8_t, uint32_t

cdef uint32_t fnvhash(bytes data)
cpdef uint8_t get_shard(bytes key, uint8_t sharding_bits, bint use_fnv_keys)
cpdef bytes get_from_tch(bytes key, list shards, int sharding_bits, bint use_fnv_keys)