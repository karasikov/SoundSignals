import pyaudio
import wave
import numpy as np
import struct
import re
import sys

def main():
    try:
        frequency = int(sys.argv[1])
        frames_shift = int(sys.argv[2])
    except:
        print "Usage: python", sys.argv[0], "<frequency> <frames_shift>"
        exit(1)

    #instantiate PyAudio
    p = pyaudio.PyAudio()
    #open stream
    rate = 176400 / 2
    stream = p.open(format=p.get_format_from_width(2),
                    channels=1,
                    rate=rate,
                    output=True)

    #original signal
    d = np.array(65535 * (1 + np.sin(2 * np.pi * np.arange(10 ** 5, dtype=np.float64) * frequency / rate)) / 2, dtype=int)

    #new signal
    phi = 0.1
    d_minus = 65535 - np.array(65535 * (1 + np.sin(2 * np.pi * np.arange(10 ** 5, dtype=np.float64) * frequency / rate + phi)) / 2, dtype=int)
    # d_minus = d_minus[:-frames_shift]
    # result = np.insert(d, np.arange(frames_shift, len(d_minus)), d_minus)
    result = d + ...np.abs((d_minus + d) / 2 - 32768)
    print (result != 0).sum()
    print result[0:100]
    s_new = ''.join([struct.pack("<H", x) for x in result])
    stream.write(s_new)

    #stop stream
    stream.stop_stream()
    stream.close()

    #close PyAudio
    p.terminate()

main()