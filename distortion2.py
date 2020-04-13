from pyo import *

s = Server().boot()

path = os.path.join(os.path.expanduser("~"), "Desktop", "testAudio2.wav")

# stereo playback with a slight shift between the two channels.
sf = SfPlayer(path, speed=[1, 1], loop=True, mul=0.4)
d = Freeverb(sf, size=0.5, damp=0.5, bal=0.5, mul=1, add=0)
rev = STRev(sf, inpos=0.25, revtime=2, cutoff=5000, bal=0.25, roomSize=1)
harm = Harmonizer(sf, transpo=-5, winsize=0.05)
#lfo = Sine(freq=[.2,.25], mul=.5, add=.5)
d = Disto(harm, drive=20, slope=0.5, mul=5).out()
chor = Chorus(d, depth=[1.5,1.6], feedback=0.5, bal=0.5).out()
s.gui(locals())