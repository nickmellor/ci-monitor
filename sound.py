#!usr/bin/env python

import os
import pyaudio
import wave

# define stream chunk
chunk = 1024  


def playwav(wav_filename):
    # open a wav format music
    f = wave.open(os.path.join('sounds', wav_filename),"rb")

    # instantiate PyAudio
    p = pyaudio.PyAudio()  

    # open stream
    stream = p.open(format=p.get_format_from_width(f.getsampwidth()),
                    channels=f.getnchannels(),
                    rate=f.getframerate(),
                    output=True)
    # read data
    data = f.readframes(chunk)  

    # play stream
    while data != '':  
        stream.write(data)  
        data = f.readframes(chunk)  

    # stop stream
    stream.stop_stream()  
    stream.close()  

    # close PyAudio
    p.terminate()

if __name__ == '__main__':
    playwav('applause.wav')