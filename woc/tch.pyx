# cython: language_level=3str, wraparound=False, boundscheck=False, nonecheck=False, profile=True

# SPDX-License-Identifier: GPL-3.0-or-later
# @authors: Runzhi He <rzhe@pku.edu.cn>
# @date: 2024-01-17

from libc.stdint cimport uint8_t, uint32_t, uint64_t
from libc.stdlib cimport free
from threading import Lock

from .base import WocKeyError

cdef extern from 'Python.h':
    object PyBytes_FromStringAndSize(char *s, Py_ssize_t len)

cdef extern from 'tchdb.h':
    ctypedef struct TCHDB:  # type of structure for a hash database
        pass

    cdef enum:  # enumeration for open modes
        HDBOREADER = 1 << 0,  # open as a reader
        HDBONOLCK = 1 << 4,  # open without locking

    const char *tchdberrmsg(int ecode)
    TCHDB *tchdbnew()
    int tchdbecode(TCHDB *hdb)
    bint tchdbopen(TCHDB *hdb, const char *path, int omode)
    bint tchdbclose(TCHDB *hdb)
    void *tchdbget(TCHDB *hdb, const void *kbuf, int ksiz, int *sp)
    bint tchdbiterinit(TCHDB *hdb)
    void *tchdbiternext(TCHDB *hdb, int *sp)

cdef uint32_t fnvhash(bytes data):
    """
    Returns the 32 bit FNV-1a hash value for the given data.
    >>> hex(fnvhash('foo'))
    '0xa9f37ed7'
    """
    # PY: 5.8usec Cy: 66.8ns
    cdef:
        uint32_t hval = 0x811c9dc5
        uint8_t b
    for b in data:  
        hval ^= b
        hval *= 0x01000193
    return hval


cdef class Hash:
    """Object representing a Tokyocabinet Hash table"""
    cdef TCHDB* _db
    cdef bytes filename

    def __cinit__(self, char *path, nolock=True):
        cdef int mode = HDBOREADER
        if nolock:
            mode |= HDBONOLCK
        self._db = tchdbnew()
        self.filename = path
        if self._db is NULL:
            raise MemoryError()
        cdef bint result = tchdbopen(self._db, path, mode)
        if not result:
            raise IOError('Failed to open .tch file "%s": ' % self.filename
                          + self._error())

    def _error(self):
        cdef int code = tchdbecode(self._db)
        cdef bytes msg = tchdberrmsg(code)
        return msg.decode('ascii')

    def __iter__(self):
        cdef:
            bint result = tchdbiterinit(self._db)
            char *buf
            int sp
            bytes key
        if not result:
            raise IOError('Failed to iterate .tch file "%s": ' % self.filename
                          + self._error())
        while True:
            buf = <char *>tchdbiternext(self._db, &sp)
            if buf is NULL:
                break
            key = PyBytes_FromStringAndSize(buf, sp)  
            free(buf)
            yield key

    cdef bytes read(self, bytes key):
        cdef:
            char *k = key  
            char *buf
            int sp
            int ksize=len(key)
        buf = <char *>tchdbget(self._db, k, ksize, &sp)
        if buf is NULL:
            raise WocKeyError(key, self.filename.decode('utf-8'))
        cdef bytes value = PyBytes_FromStringAndSize(buf, sp)  
        free(buf)
        return value

    def __getitem__(self, bytes key):
        return self.read(key)

    def __del__(self):
        cdef bint result = tchdbclose(self._db)
        if not result:
            raise IOError('Failed to close .tch "%s": ' % self.filename
                          + self._error())

    def __dealloc__(self):
        free(self._db)


# Pool of open TokyoCabinet databases to save few milliseconds on opening
cdef dict _TCH_POOL = {}  # type: Dict[str, Hash]
TCH_LOCK = Lock()

cdef _get_tch(char *path):
    """ Cache Hash() objects """
    if path in _TCH_POOL:
        return _TCH_POOL[path]
    try:
        TCH_LOCK.acquire()
        # in multithreading environment this can cause race condition,
        # so we need a lock
        if path not in _TCH_POOL:
            _TCH_POOL[path] = Hash(path)  
    finally:
        TCH_LOCK.release()
    return _TCH_POOL[path]

cpdef uint8_t get_shard(bytes key, uint8_t sharding_bits, bint use_fnv_keys):
    """ Get shard id """
    cdef uint8_t p
    if use_fnv_keys:
        p = fnvhash(key)  
    else:
        p = key[0]
    cdef uint8_t prefix = p & (2**sharding_bits - 1)
    return prefix

cpdef bytes get_from_tch(bytes key, list shards, int sharding_bits, bint use_fnv_keys):
    return _get_tch(
        shards[get_shard(key, sharding_bits, use_fnv_keys)].encode('utf-8')
    )[key] 
