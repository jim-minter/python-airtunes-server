#!/usr/bin/python

import ctypes
import sys

libalac = ctypes.CDLL("../libalac/libalac.so", use_errno=True)
encoder = libalac.init()

def get_next_frame():
    data = sys.stdin.read(352 * 2 * 2)
    if not data:
        raise Exception()

    out = ctypes.create_string_buffer(4096)
    l = ctypes.c_int(len(data))

    libalac.encode(encoder, data, out, ctypes.byref(l))

    return out[:l.value]

def deinit():
    libalac.deinit(encoder)
