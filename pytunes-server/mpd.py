#!/usr/bin/python

import socket

class Mpd(object):
    def __init__(self, host):
        self.s = socket.create_connection((host, 6600))
        self.f = self.s.makefile()
        if not self.f.readline().startswith("OK "):
            raise Exception()

    def read(self):
        h = {}
        for line in self.f:
            line = line.strip()
            if line == "OK":
                break
            line = line.split(": ", 1)
            h[line[0]] = line[1]
        return h

    def send(self, cmd):
        print >>self.f, cmd
        self.f.flush()
        return self.read()
