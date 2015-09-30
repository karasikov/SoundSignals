#!usr/bin/env python
#coding=utf-8

import pyaudio
import wave
import numpy as np
import struct
import re
import sys

def main():
    try:
        wav_file = sys.argv[1]
        frames_shift = int(sys.argv[2])
    except:
        print "Usage: python", sys.argv[0], "<wav_file> <frames_shift>"
        exit(1)

    #open a wav format music
    f = wave.open(wav_file, "rb")
    #instantiate PyAudio
    p = pyaudio.PyAudio()
    #open stream
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=1,
                    rate=f.getnchannels() * f.getframerate(),
                    output=True)

    #read data
    s = f.readframes(10 ** 5)
    d = np.array([struct.unpack("<H", s[2 * i : 2 * i + 2])[0]
                        for i in range(len(s) / 2)])
    d_inverted = 65535 - d
    result = d[frames_shift:]

    # print result[0:100]
    s_new = ''.join([struct.pack("<H", x) for x in result])
    stream.write(s_new)

    #stop stream
    stream.stop_stream()
    stream.close()

    #close PyAudio
    p.terminate()

main()