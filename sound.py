#!usr/bin/env python

import os
import pyaudio
import wave

chunksize = 1024


def playwav(wav_filename):
    wav_file = wave.open(os.path.join('sounds', wav_filename),"rb")
    audio_session = pyaudio.PyAudio()
    stream = audio_session.open(format=audio_session.get_format_from_width(wav_file.getsampwidth()),
                                channels=wav_file.getnchannels(), rate=wav_file.getframerate(),
                                output=True)
    data = wav_file.readframes(chunksize)
    while data != '':
        stream.write(data)  
        data = wav_file.readframes(chunksize)
    stream.stop_stream()
    stream.close()  
    audio_session.terminate()

if __name__ == '__main__':
    playwav('applause.wav')
