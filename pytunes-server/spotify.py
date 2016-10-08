#!/usr/bin/python

import dbus
import requests
import struct

class Spotify(object):
    def __init__(self):
        bus = dbus.SessionBus()
        proxy = bus.get_object("org.mpris.MediaPlayer2.spotify",
                               "/org/mpris/MediaPlayer2")
        self.iface = dbus.Interface(proxy,
                                    dbus_interface="org.mpris.MediaPlayer2.Player")
        self.jpegcache = (None, None)


    def query(self):
        dct = self.iface.Get("org.mpris.MediaPlayer2.Player", "Metadata",
                             dbus_interface="org.freedesktop.DBus.Properties")

        if self.jpegcache[0] != dct["mpris:artUrl"]:
            self.jpegcache = (dct["mpris:artUrl"],
                              requests.get(dct["mpris:artUrl"]).content)

        return {"Title": str(dct["xesam:title"]),
                "Artist": str(dct["xesam:artist"][0]),
                "Album": str(dct["xesam:album"]),
                "Jpeg": self.jpegcache[1]}
