#!/usr/bin/python

import argparse
import clock
import collections
import os
import SocketServer
import socket
import struct
import threading
import time


class RTSPBase(object):
    def __init__(self, remote_address):
        self.remote_address = remote_address
        self.cseq = 1

        s = socket.create_connection(self.remote_address)
        self.local_address = s.getsockname()
        self.f = s.makefile()

    def _send_request(self, verb, url, h, body=None):
        h["CSeq"] = self.cseq
        if body:
            h["Content-Length"] = len(body)

        self.f.write("%s %s RTSP/1.0\r\n" % (verb, url))
        for k in h:
            self.f.write("%s: %s\r\n" % (k, h[k]))
        self.f.write("\r\n")

        if body:
            self.f.write(body)

        self.f.flush()
        self.cseq += 1

    def _read_response(self):
        status = self.f.readline().strip().split(" ")
        status[1] = int(status[1])

        h = {}
        while True:
            l = self.f.readline().strip()
            if not l:
                break
            h.update([l.split(": ", 1)])

        body = None
        if "Content-Length" in h:
            body = self.f.read(int(h["Content-Length"]))

        return (status, h, body)

    def request(self, verb, url, h, body=None):
        self._send_request(verb, url, h, body)
        return self._read_response()


class RTSP(RTSPBase):
    def __init__(self, remote_address):
        super(RTSP, self).__init__(remote_address)
        self.session_id = "3509167977"
        self.url = "rtsp://%s/%s" % (self.local_address[0], self.session_id)
        self.seq = 0
        self.rtptime = 0.25 * 44100
        self.do_announce()
        self.do_setup()
        self.do_record()

    def request(self, verb, url, h, body=None):
        rv = super(RTSP, self).request(verb, url, h, body)

        if rv[0][1] != 200:
            raise Exception()

        return rv

    def do_announce(self):
        body = """v=0
o=iTunes %(session_id)s 0 IN IP4 %(ip)s
s=iTunes
c=IN IP4 %(ip)s
t=0 0
m=audio 0 RTP/AVP 96
a=rtpmap:96 AppleLossless
a=fmtp:96 352 0 16 40 10 14 2 255 0 0 44100""" % {"session_id": self.session_id, "ip": self.local_address[0]}

        self.request("ANNOUNCE", self.url, {"Content-Type": "application/sdp"},
                     body)

    def do_setup(self):
        (status, h, body) = self.request("SETUP", self.url,
                                         {"Transport": "RTP/AVP/UDP;unicast;interleaved=0-1;mode=record;control_port=6001;timing_port=6002"})

        for v in [v.split("=") for v in h["Transport"].split(";")]:
            if v[0] in ["server_port", "control_port", "timing_port"]:
                setattr(self, "remote_" + v[0], int(v[1]))

    def do_record(self):
        self.request("RECORD", self.url,
                     {"Session": "1", "Range": "npt=0-",
                      "RTP-Info": "seq=%u;rtptime=%u" % (self.seq,
                                                         self.rtptime)})

    def set_volume(self, volume):
        self.request("SET_PARAMETER", self.url,
                     {"Session": "1", "Content-Type": "text/parameters"},
                     "volume: %s\r\n" % volume)

    def do_flush(self):
        self.request("FLUSH", self.url,
                     {"Session": "1", "RTP-Info": "seq=%u;rtptime=%u" % (self.seq, self.rtptime)})


class TimingHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        reply = "80d3000700000000".decode("hex") + data[24:32] + \
                struct.pack(">Q", clock.ntpstamp()) + \
                struct.pack(">Q", clock.ntpstamp())

        self.request[1].sendto(reply, self.client_address)


class ControlHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data = self.request[0]

        (seq, count) = struct.unpack(">HH", data[4:8])
        with loglock:
            for i in log:
                if i[0] >= seq and i[0] < seq + count:
                    self.request[1].sendto(i[1], (rtsp.remote_address[0],
                                                  rtsp.remote_server_port))


def send_sync(rtsp, first=False):
    if(first):
        data = "90d40007".decode("hex")
    else:
        data = "80d40007".decode("hex")

    data += struct.pack(">LQL", rtsp.rtptime - 0.25 * 44100, clock.ntpstamp(),
                        rtsp.rtptime)

    controlserver.socket.sendto(data, (rtsp.remote_address[0],
                                       rtsp.remote_control_port))


def send_data(rtsp, alac, first=False):
    if(first):
        data = "80e0".decode("hex")
    else:
        data = "8060".decode("hex")

    data += struct.pack(">HL", rtsp.seq, rtsp.rtptime) + "3dab38c9".decode("hex") + alac

    with loglock:
        log.append((rtsp.seq, data))

    controlserver.socket.sendto(data, (rtsp.remote_address[0],
                                       rtsp.remote_server_port))

    rtsp.seq = (rtsp.seq + 1) & 0xFFFF
    rtsp.rtptime += 352


loglock = threading.Lock()
log = collections.deque(maxlen=int(0.25 * 44100 / 352))

controlserver = SocketServer.UDPServer(("0.0.0.0", 6001), ControlHandler)
controlserver_thread = threading.Thread(target=controlserver.serve_forever)
controlserver_thread.daemon = True
controlserver_thread.start()

timingserver = SocketServer.UDPServer(("0.0.0.0", 6002), TimingHandler)
timingserver_thread = threading.Thread(target=timingserver.serve_forever)
timingserver_thread.daemon = True
timingserver_thread.start()


def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("-d", metavar="device")
    ap.add_argument("-s", metavar="stream")
    ap.add_argument("host")
    ap.add_argument("port")
    return ap.parse_args()


def main():
    global rtsp

    args = parse_args()
    args.host = socket.gethostbyname(args.host)

    if args.d:
        import alsa
        alsa.init(args.d)

    elif args.s:
        import pulse
        pulse.init(args.s)

    else:
        import stdin

    rtsp = RTSP((args.host, int(args.port)))

    first = True
    last_sync = 0
    last_mtime = 0
    seq = 1
    start = clock.now()
    try:
        while True:
            now = clock.now()
            if now - last_sync > 1:
                send_sync(rtsp, first)
                last_sync = now

            mtime = os.stat(os.path.dirname(__file__) + "/.volume").st_mtime
            if last_mtime != mtime:
                rtsp.set_volume(open(os.path.dirname(__file__) + "/.volume").read().strip())
                last_mtime = mtime

            if args.d:
                send_data(rtsp, alsa.get_next_frame(), first)

            elif args.s:
                send_data(rtsp, pulse.get_next_frame(), first)

            else:
                send_data(rtsp, stdin.get_next_frame(), first)
                delay = start + (seq * 352.0/44100) - now
                if delay > 0:
                    time.sleep(delay)

            first = False
            seq += 1

    except EOFError:
        pass

    time.sleep(2)
    rtsp.do_flush()
    alsa.deinit()

if __name__ == "__main__":
    main()
