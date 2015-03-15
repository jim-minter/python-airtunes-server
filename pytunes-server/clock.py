#!/usr/bin/python

import ctypes
import os

CLOCK_MONOTONIC_RAW = 4 # <linux/time.h>

class Timespec(ctypes.Structure):
    _fields_ = [
        ("tv_sec", ctypes.c_long),
        ("tv_nsec", ctypes.c_long)
    ]

def gettime():
    t = Timespec()
    if librt.clock_gettime(CLOCK_MONOTONIC_RAW , ctypes.byref(t)):
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))

    return t

def now():
    t = gettime()
    return t.tv_sec + t.tv_nsec / 1e9

def ntpstamp():
    t = gettime()
    return (2208988800 + t.tv_sec << 32) + (2**32 * t.tv_nsec / 1e9)

librt = ctypes.CDLL("librt.so", use_errno=True)
