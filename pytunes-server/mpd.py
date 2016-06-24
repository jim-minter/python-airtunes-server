#!/usr/bin/python

import socket

class Mpd(object):
    def __init__(self, host):
        self.host = host

    def currentsong(self):
        s = socket.create_connection((self.host, 6600))
        f = s.makefile()
        if not f.readline().startswith("OK "):
            raise Exception()

        print >>f, "currentsong"
        f.flush()
        h = {}
        for line in f:
            line = line.strip()
            if line == "OK":
                break
            line = line.split(": ", 1)
            h[line[0]] = line[1]
        return h
