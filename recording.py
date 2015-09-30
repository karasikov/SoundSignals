from sys import byteorder
from struct import pack

import pyaudio
import wave
import time
import numpy as np

CHUNK_SIZE = 50
FORMAT = pyaudio.paInt16
RATE = 44100

ENHANCEMENT = 1
THRESHOLD = 100

def normalize(sound_signal):
    """Normalize the volume out"""
    MAXIMUM = 16384
    ratio = float(MAXIMUM) / abs(sound_signal).max()
    return np.asarray(sound_signal * ratio, dtype=np.int16)

def trim(sound_signal):
    """Trim the blank spots at the start and end"""
    begin, end = np.where(abs(sound_signal) > THRESHOLD)[0][[0, -1]]
    return sound_signal[begin:end]

def add_silence(sound_signal, seconds):
    """Add silence to the start and end of |sound_signal| of length |seconds| (float)"""
    return np.lib.pad(sound_signal, int(seconds * RATE), 'constant')

def record(duration=4.):
    """
    Record a word or words from the microphone and 
    return the data as an array of signed shorts.

    Normalizes the audio, trims silence from the 
    start and end, and pads with 0.5 seconds of 
    blank sound to make sure VLC et al can play 
    it without getting chopped off.
    """
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT, channels=1, rate=RATE,
                    input=True, output=True,
                    frames_per_buffer=CHUNK_SIZE)

    recorded_signal = np.array([], dtype=np.int16)

    start = time.time()

    for i in range(int(duration * RATE / CHUNK_SIZE)):
        recorded_chunk = np.fromstring(stream.read(CHUNK_SIZE), dtype=np.dtype('<h'))
        recorded_signal = np.append(recorded_signal, recorded_chunk)

        sending_chunk = recorded_chunk * ENHANCEMENT
        sending_chunk = sending_chunk.clip(-32000, 32000)
        stream.write(sending_chunk.tostring())

    print("recording lasted " + str(time.time() - start) + " sec")

    sample_width = p.get_sample_size(FORMAT)
    stream.stop_stream()
    stream.close()
    p.terminate()

    recorded_signal = normalize(recorded_signal)
    recorded_signal = trim(recorded_signal)
    recorded_signal = add_silence(recorded_signal, 0.5)
    return sample_width, recorded_signal

def record_to_file(path):
    """Records from the microphone and outputs the resulting data to |path|"""
    sample_width, recorded_signal = record()

    wf = wave.open(path, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(sample_width)
    wf.setframerate(RATE)
    wf.writeframes(recorded_signal.astype(np.dtype('<h')).tostring())
    wf.close()

if __name__ == '__main__':
    print("please speak a word into the microphone")
    record_to_file('demo.wav')
    print("result written to demo.wav")