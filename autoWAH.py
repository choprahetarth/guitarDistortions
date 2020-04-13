from pyo import *
import os

s = Server().boot()
s.start()

soundfile = os.path.join(os.path.expanduser("~"), "Desktop", "testAudio2.wav")
src = SfPlayer(soundfile, loop=True).mix(2)
fol = Follower(src, freq=30, mul=4000, add=40)
f = Biquad(src, freq=fol, q=5, type=2).out()

s.gui()
