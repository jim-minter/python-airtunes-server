#!/usr/bin/python

import socket

class Mpd(object):
    def __init__(self, host):
        self.s = socket.create_connection((host, 6600))
        self.f = self.s.makefile()
        if not self.f.readline().startswith("OK "):
            raise Exception()

    def currentsong(self):
        print >>self.f, "currentsong"
        self.f.flush()
        h = {}
        for line in self.f:
            line = line.strip()
            if line == "OK":
                break
            line = line.split(": ")
            h[line[0]] = line[1]
        return h
