# cython: language_level=3str, wraparound=False, boundscheck=False, nonecheck=False, profile=True, linetrace=True

# SPDX-License-Identifier: GPL-3.0-or-later
# @authors: Runzhi He <rzhe@pku.edu.cn>
# @date: 2024-01-17

from libc.stdint cimport uint8_t, uint32_t, uint64_t
from libc.stdlib cimport free

cdef extern from 'Python.h':
    object PyBytes_FromStringAndSize(char *s, Py_ssize_t len)

cdef extern from 'tchdb.h':
    ctypedef struct TCHDB:  # type of structure for a hash database
        pass

    cdef enum:  # enumeration for open modes
        HDBOREADER = 1 << 0,                   # open as a reader
        HDBOWRITER = 1 << 1,                   # open as a writer
        HDBOCREAT = 1 << 2,                    # writer creating
        HDBOTRUNC = 1 << 3,                    # writer truncating
        HDBONOLCK = 1 << 4,                    # open without locking

    const char *tchdberrmsg(int ecode)  #  Get the message string corresponding to an error code
    TCHDB *tchdbnew()  # Create a hash database object
    int tchdbecode(TCHDB *hdb)  # Set the error code of a hash database object
    bint tchdbopen(TCHDB *hdb, const char *path, int omode)
    bint tchdbclose(TCHDB *hdb)  # Close a hash database object
    void tchdbdel(TCHDB *hdb)  # Delete a hash database object
    void *tchdbget(TCHDB *hdb, const void *kbuf, int ksiz, int *sp)
    bint tchdbiterinit(TCHDB *hdb)  # Initialize the iterator of a hash database object
    void *tchdbiternext(TCHDB *hdb, int *sp)  # Get the next key of the iterator of a hash database object
    bint tchdbput(TCHDB *hdb, const void *kbuf, int ksiz, const void *vbuf, int vsiz)  # Store a new record into a hash database object
    bint tchdbout(TCHDB *hdb, const void *kbuf, int ksiz)  # Remove a record of a hash database object
    uint64_t tchdbrnum(TCHDB *hdb)  # Get the number of records of a hash database object
    bint tchdbvanish(TCHDB *hdb)  # Remove all records of a hash database object

cdef class TCHashDB:
    """Object representing a Tokyocabinet Hash table"""

    def __cinit__(self, str path, bint ro=False):
        self.filename = path
        _encoded = path.encode()
        cdef char* dbpath = _encoded

        cdef int mode = 0
        if not ro:  # write mode: create if not exists
            mode |= HDBOWRITER
            mode |= HDBOCREAT
        else:  # read mode: disable locks
            mode |= HDBOREADER
            mode |= HDBONOLCK

        self._db = tchdbnew()
        if self._db is NULL:
            raise MemoryError()
        cdef bint result = tchdbopen(self._db, dbpath, mode)
        if not result:
            raise IOError(f'Failed to open {self.filename}: ' + self._error())

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
            raise IOError(f'Failed to iterate {self.filename}: ' + self._error())
        while True:
            buf = <char *>tchdbiternext(self._db, &sp)
            if buf is NULL:
                break
            key = PyBytes_FromStringAndSize(buf, sp)
            free(buf)
            yield key

    cpdef bytes get(self, bytes key):
        cdef:
            char *k = key
            char *buf
            int sp
            int ksize=len(key)
        buf = <char *>tchdbget(self._db, k, ksize, &sp)
        if buf is NULL:
            raise KeyError(f'Key {key.hex()} not found in {self.filename}')
        cdef bytes value = PyBytes_FromStringAndSize(buf, sp)
        free(buf)
        return value

    cpdef void put(self, bytes key, bytes value) except *:
        cdef:
            char *k = key
            int ksize = len(key)
            char *v = value
            int vsize = len(value)
            bint result
        result = tchdbput(self._db, k, ksize, v, vsize)
        if not result:
            raise IOError(f'Failed to put {key.hex()} in {self.filename}: ' + self._error())

    cpdef void delete(self, bytes key) except *:
        cdef:
            char *k = key
            int ksize = len(key)
            bint result
        result = tchdbout(self._db, k, ksize)
        if not result:
            raise IOError(f'Failed to delete {key.hex()} in {self.filename}: ' + self._error())

    cpdef void drop(self) except *:
        cdef:
            bint result
        result = tchdbvanish(self._db)
        if not result:
            raise IOError(f'Failed to drop all records in {self.filename}: ' + self._error())

    cpdef void close(self) except *:
        cdef bint result = tchdbclose(self._db)
        if not result:
            raise IOError(f'Failed to close {self.filename}: ' + self._error())

    def __getitem__(self, bytes key):
        return self.get(key)

    def __setitem__(self, bytes key, bytes value):
        self.put(key, value)

    def __delitem__(self, bytes key):
        self.delete(key)

    def __len__(self):
        return tchdbrnum(self._db)

    def __del__(self):
        self.close()

    def __dealloc__(self):
        free(self._db)  # it should never be null
