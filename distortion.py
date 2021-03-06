from pyo import *

s = Server().boot()

SOURCE = os.path.join(os.path.expanduser("~"), "Desktop", "testAudio2.wav")

#hello = Sig(0.99)
#hello.ctrl(title="CENTRAL FREQ")
#hello1 = Sig(0.99)
#hello1.ctrl(title="BP Q ")
#hello2 = Sig(0.99)
#hello2.ctrl(title="Boost")
#hello3 = Sig(0.99)
#hello3.ctrl(title="LP_CUTOFF_FREQ")
#hello4 = Sig(0.99)
#hello4.ctrl(title="LP_CUTOFF_FREQ")
# Distortion parameters
#BP_CENTER_FREQ = hello*100
#BP_Q = hello1*10
#BOOST = hello2*100
#LP_CUTOFF_FREQ = hello3*1000
BP_CENTER_FREQ = 400        # Bandpass filter center frequency.\
BP_Q = 4                   # Bandpass Q (center_freq / Q = bandwidth).
BOOST = 300                 # Pre-boost (linear gain).
LP_CUTOFF_FREQ = 6000       # Lowpass filter cutoff frequency.
BALANCE = 0.8    # Balance dry - wet.

src = SfPlayer(SOURCE, loop=True).mix(2)

# The transfert function is build in two phases.

# 1. Transfert function for signal lower than 0.
table = ExpTable([(0,-.25),(4096,0),(8192,0)], exp=30)

# 2. Transfert function for signal higher than 0.
# First, create an exponential function from 1 (at the beginning of the table)
# to 0 (in the middle of the table).
high_table = ExpTable([(0,1),(2000,1),(4096,0),(4598,0),(8192,0)],
                      exp=5, inverse=False)
# Then, reverse the table’s data in time, to put the shape in the second 
# part of the table.
high_table.reverse()

# Finally, add the second table to the first, point by point.
table.add(high_table)

# Show the transfert function.
table.view(title="Transfert function")

# Bandpass filter and boost gain applied on input signal.
bp = ButBP(src, freq=BP_CENTER_FREQ, q=BP_Q)
boost = Sig(bp, mul=BOOST)

# Apply the transfert function.
sig = Lookup(table, boost)

# Lowpass filter on the distorted signal.
lp = ButLP(sig, freq=LP_CUTOFF_FREQ, mul=.7)

# Balance between dry and wet signals.
mixed = Interp(src, lp, interp=BALANCE)

# Send the signal to the outputs.
out = (mixed * 0.3).out()

# Show the resulting waveform.
sc = Scope(mixed)
s.gui(locals())