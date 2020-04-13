import pyaudio
import numpy as np
import pylab
import matplotlib.pyplot as plt
from scipy.io import wavfile
import time
import sys
import seaborn as sns
import serial
from time import perf_counter

ser = serial.Serial()
ser.port = "/dev/cu.usbmodem14101"
ser.baudrate = 9600
ser.bytesize = serial.EIGHTBITS #number of bits per bytes
ser.parity = serial.PARITY_NONE #set parity check: no parity
ser.stopbits = serial.STOPBITS_TWO #number of stop bits
ser.open()

i=0
f,ax = plt.subplots(2)
audio_average = 0
dfft_mean = 0
xs = []
ys = []
low_freq_avg_list =[]
y_avg=0
prev_beat=0
bpm_list = []
curr_time = 0
bpm = 0

# Prepare the Plotting Environment with random starting values
x = np.arange(10000)
y = np.random.randn(10000)

# Plot 0 is for raw audio data
li, = ax[0].plot(x, y)
ax[0].set_xlim(0,1000)
ax[0].set_ylim(-5000,5000)
ax[0].set_title("Raw Audio Signal")
# Plot 1 is for the FFT of the audio
li2, = ax[1].plot(x, y)
ax[1].set_xlim(0,5000)
ax[1].set_ylim(-100,100)
ax[1].set_title("Fast Fourier Transform")
# Show the plot, but without blocking updates
#plt.pause(0.01)
plt.tight_layout()

FORMAT = pyaudio.paInt16 # We use 16bit format per sample
CHANNELS = 1
RATE = 44100
CHUNK = 1024 # 1024bytes of data red from a buffer
RECORD_SECONDS = 0.1
WAVE_OUTPUT_FILENAME = "file.wav"

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True)#,
                    #frames_per_buffer=CHUNK)

global keep_going
keep_going = True

def plot_data(in_data):
    # get and convert the data to float
    audio_data = np.fromstring(in_data, np.int16)
    # Fast Fourier Transform, 10*log10(abs) is to scale it to dB
    # and make sure it's not imaginary
    dfft = 10.*np.log10(abs(np.fft.rfft(audio_data)))
    #print(dfft)
    xs = dfft
    ys = np.arange(len(dfft))*10.
    # Force the new data into the plot, but without redrawing axes.
    # If uses plt.draw(), axes are re-drawn every time
    #print (audio_data[0:10])
    #########################
    y_avg = np.mean(dfft)
    low_freq = [dfft[i] for i in range(len(dfft)) if ys[i] < 2000]
    low_freq_avg = np.mean(low_freq)
    global low_freq_avg_list
    low_freq_avg_list.append(low_freq_avg)
    cumulative_avg = np.mean(low_freq_avg_list)
    bass = low_freq[:int(len(low_freq)/2)]
    bass_avg = np.mean(bass)
    #print(bass_avg)
    if (y_avg > 10 and (bass_avg > cumulative_avg * 1.5 or
            (low_freq_avg < y_avg * 1.2 and bass_avg > cumulative_avg))):
        global curr_time
        global prev_beat
        global bpm
        #print("here")
        curr_time = perf_counter()
        if curr_time - prev_beat > 50/180: # 180 BPM max
            bpm = int(30 / (curr_time - prev_beat))
            print(bpm)
            ser.write(b'm')
            global bpm_list
            if len(bpm_list) < 4:
                if bpm > 30:
                    bpm_list.append(bpm)
        else:
                bpm_avg =  (np.mean(bpm_list))
                if abs(bpm_avg - bpm) < 35:
                    bpm_list.append(bpm)
        prev_beat = curr_time
    else:
        ser.write(b'h')    
    ########################
    if len(low_freq_avg_list) > 100:
        low_freq_avg_list = low_freq_avg_list[25:]
        # print("REFRESH!!")
    if len(bpm_list) > 24:
        bpm_list = bpm_list[8:]
    if y_avg < 10:
        bpm_list = []
        low_freq_avg_list = []
    #######################
    #audio_average = (sum(abs(audio_data[0:10]))/10)
    #print (audio_average)
    #if (audio_average >= 400 or audio_average < -400):
        #ser.write(b'm')
        #print("this is turned on")
    #else:
        #ser.write(b'h')
        #print("this is turned off")
    #print (dfft[0:10])
    #print
    li.set_xdata(np.arange(len(audio_data)))
    li.set_ydata(audio_data)
    li2.set_xdata(np.arange(len(dfft))*10.)
    li2.set_ydata(dfft)

    # Show the updated plot, but without blocking
    plt.pause(0.01)
    if keep_going:
        return True
    else:
        return False

# Open the connection and start streaming the data
stream.start_stream()
print ("\n+---------------------------------+")
print ("| Press Ctrl+C to Break Recording |")
print ("+---------------------------------+\n")

# Loop so program doesn't end while the stream callback's
# itself for new data
while keep_going:
    try:
        plot_data(stream.read(CHUNK,exception_on_overflow=False))
    except KeyboardInterrupt:
        exit()

# Close up shop (currently not used because KeyboardInterrupt
# is the only way to close)
stream.stop_stream()
stream.close()

audio.terminate()
