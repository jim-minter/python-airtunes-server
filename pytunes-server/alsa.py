#!/usr/bin/python

import alsaaudio
import ctypes

pcm = alsaaudio.PCM(type=alsaaudio.PCM_CAPTURE, card="hw:2,1")
pcm.setperiodsize(352)

libalac = ctypes.CDLL("../libalac/libalac.so", use_errno=True)
encoder = libalac.init()

def get_next_frame():
    data = pcm.read()[1]
    if not data:
        raise Exception()

    out = ctypes.create_string_buffer(4096)
    l = ctypes.c_int(len(data))

    libalac.encode(encoder, data, out, ctypes.byref(l))

    return out[:l.value]

def deinit():
    libalac.deinit(encoder)
