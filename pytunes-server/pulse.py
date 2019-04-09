#!/usr/bin/python

import ctypes
import os


class pa_sample_spec(ctypes.Structure):
    _fields_ = [('format', ctypes.c_int),
                ('rate', ctypes.c_uint32),
                ('channels', ctypes.c_uint8)]


class pa_buffer_attr(ctypes.Structure):
    _fields_ = [('maxlength', ctypes.c_uint32),
                ('tlength', ctypes.c_uint32),
                ('prebuf', ctypes.c_uint32),
                ('minreq', ctypes.c_uint32),
                ('fragsize', ctypes.c_uint32)]

def get_next_frame():
    data = ctypes.create_string_buffer(352 * 2 * 2)
    libpulse.pa_simple_read(ctypes.c_void_p(pcm), data, 352 * 2 * 2, None)

    out = ctypes.create_string_buffer(4096)
    l = ctypes.c_int(len(data))

    libalac.encode(ctypes.c_void_p(encoder), data, out, ctypes.byref(l))

    return out[:l.value]


def init(stream):
    global pcm

    pcm = libpulse.pa_simple_new(None, "pytunes-server", 2, stream, "monitor",
                                 ctypes.byref(pa_sample_spec(3, 44100, 2)), None,
                                 ctypes.byref(pa_buffer_attr(-1, -1, -1, -1, 352 * 2 * 2)),
                                 None)


def deinit():
    libalac.deinit(ctypes.c_void_p(encoder))
    libpulse.pa_simple_free(ctypes.c_void_p(pcm))


libalac = ctypes.CDLL(os.path.dirname(__file__) + "/../libalac/libalac.so",
                      use_errno=True)
libalac.init.restype = ctypes.c_void_p
encoder = libalac.init()

libpulse = ctypes.CDLL("/lib64/libpulse-simple.so.0", use_errno=True)
libpulse.pa_simple_new.restype = ctypes.c_void_p
