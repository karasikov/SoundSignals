from sys import byteorder
from struct import pack

import pyaudio
import wave
import time
import numpy as np

CHUNK_SIZE = 1
FORMAT = pyaudio.paInt16
RATE = 44100

ENHANCEMENT = 2
THRESHOLD = 100

def callback(in_data, frame_count, time_info, status):
    recorded_chunk = np.fromstring(in_data, dtype=np.dtype('<h'))
    sending_chunk = (recorded_chunk.astype(np.int64) * ENHANCEMENT).clip(-32000, 32000)
    return sending_chunk.astype(np.dtype('<h')).tostring(), pyaudio.paContinue

if __name__ == '__main__':
    print("please speak a word into the microphone")

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=1,
                    rate=RATE,
                    input=True, output=True,
                    frames_per_buffer=CHUNK_SIZE,
                    stream_callback=callback)

    src_latency = 1000.0 * stream.get_input_latency()
    buffer_latency = 1000.0 * CHUNK_SIZE / RATE
    dst_latency = 1000.0 * stream.get_output_latency()
    total_latency = buffer_latency + dst_latency + src_latency

    print("Expected latency: %.2fms (%0.1f, %0.1f, %0.1f)" % (
            total_latency, src_latency, buffer_latency, dst_latency))

    while stream.is_active():
        time.sleep(0.05)

    stream.stop_stream()
    stream.close()
    p.terminate()
