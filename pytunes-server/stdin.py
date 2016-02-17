#!/usr/bin/python

import ctypes
import sys
import os


def get_next_frame():
    data = sys.stdin.read(352 * 2 * 2)
    if not data:
        raise EOFError()

    out = ctypes.create_string_buffer(4096)
    l = ctypes.c_int(len(data))

    libalac.encode(ctypes.c_void_p(encoder), data, out, ctypes.byref(l))

    return out[:l.value]


def deinit():
    libalac.deinit(ctypes.c_void_p(encoder))


libalac = ctypes.CDLL(os.path.dirname(__file__) + "/../libalac/libalac.so",
                      use_errno=True)
libalac.init.restype = ctypes.c_void_p
encoder = libalac.init()
