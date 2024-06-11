# cython: language_level=3str, wraparound=False, boundscheck=False, nonecheck=False, profile=True, linetrace=True

cdef extern from 'tchdb.h':
    ctypedef struct TCHDB:  # type of structure for a hash database
        pass

cdef class TCHashDB:
    cdef TCHDB* _db
    cdef str filename

    """Object representing a Tokyocabinet Hash table"""
    cpdef bytes get(self, bytes key)
    cpdef void put(self, bytes key, bytes value) except *
    cpdef void delete(self, bytes key) except *
    cpdef void drop(self) except *
    cpdef void close(self) except *
