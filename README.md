# python-airtunes-server

At the very least, this works well on Fedora against a Philips AD7050W...

### To discover IP and port of airtunes speaker:

```
$ avahi-browse -ar
+ eth0 IPv4 0025D10C55B4@Philips AD7050W 0C55B4           AirTunes Remote Audio local
= eth0 IPv4 0025D10C55B4@Philips AD7050W 0C55B4           AirTunes Remote Audio local
   hostname = [Philips-AD7050W-0C55B4.local]
   address = [192.168.1.24]
   port = [1026]
   txt = ["fv=s9219.102.10032" "am=AD7050W" "vs=141.9" "vn=65537" "tp=UDP" "ss=16" "sr=44100" "sv=false" "pw=false" "ft=0x44C0A00" "et=0,4" "da=true" "cn=0,1" "ch=2" "txtvers=1"]
^C
Got SIGINT, quitting.
```

In the above example, the IP is 192.168.1.24 and the port is 1026.

### To play CD (16-bit little endian, 44.1kHz, stereo) samples from stdin:

```
$ mpg123 -e s16 -r 44100 --stereo -s $FILE.mp3 | ./server.py $IP $PORT
$ arecord [-D hw:$DEVICE] -t raw -f cd | ./server.py $IP $PORT
```

### To play CD samples from another ALSA device:

```
$ ./server.py -d hw:$DEVICE $IP $PORT
```

### To play CD samples via ALSA snd-aloop:

```
$ sudo modprobe snd-aloop
$ ./server.py -d hw:Loopback,1 $IP $PORT &

$ aplay -D hw:Loopback -t raw -f cd $FILE.pcm
$ mplayer -ao alsa:device=hw=Loopback $FILE.mp3
$ mpg123 -a hw:Loopback $FILE.mp3
```

### To play CD samples via PulseAudio null-sink:

```
$ pactl load-module module-null-sink sink_name=pytunes sink_properties=device.description=PyTunes
$ ./server.py -s pytunes.monitor $IP $PORT &

$ mplayer -ao pulse::pytunes $FILE.mp3
```