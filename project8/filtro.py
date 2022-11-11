#!/usr/bin/env python3

# sudo pip install PeakUtils

import numpy as np
import sounddevice as sd
import soundfile   as sf
import matplotlib.pyplot as plt

from scipy.fftpack import fft
from scipy import signal
from scipy import signal as sg

def generateSin(freq, amplitude, time, fs):
    n = time*fs
    x = np.linspace(0.0, time, n)
    s = amplitude*np.sin(freq*x*2*np.pi)
    return (x, s)

def calcFFT(signal, fs):
    # https://docs.scipy.org/doc/scipy/reference/tutorial/fftpack.html
    N  = len(signal)
    T  = 1/fs
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)
    yf = fft(signal)
    return(xf, yf[0:N//2])

def filtro(y, samplerate, cutoff_hz):
  # https://scipy.github.io/old-wiki/pages/Cookbook/FIRFilter.html
    nyq_rate = samplerate/2
    width = 5.0/nyq_rate
    ripple_db = 60.0 #dB
    N , beta = sg.kaiserord(ripple_db, width)
    taps = sg.firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
    yFiltrado = sg.lfilter(taps, 1.0, y)
    return yFiltrado

def LPF(signal, cutoff_hz, fs):
    from scipy import signal as sg
    #####################
    # Filtro
    #####################
    # https://scipy.github.io/old-wiki/pages/Cookbook/FIRFilter.html
    nyq_rate = fs/2
    width = 5.0/nyq_rate
    ripple_db = 60.0 #dB
    N , beta = sg.kaiserord(ripple_db, width)
    taps = sg.firwin(N, cutoff_hz/nyq_rate, window=('kaiser', beta))
    return( sg.lfilter(taps, 1.0, signal))

def main():
    fs = 44100
    sd.default.samplerate = fs
    sd.default.channels = 1
    
    audio, samplerate = sf.read('mario.wav')
    sd.play(data=audio, samplerate=samplerate)
    sd.wait()

    audio_time = len(audio)/samplerate
    yAudio = audio[:,1]
    samplesAudio = len(yAudio)


    yfiltrado = LPF(audio, 2200, fs)
    sd.play(yfiltrado)
    sd.wait()

    #####################
    # Normaliza audio
    #####################
    audioMax = np.max(np.abs(yAudio))
    yAudioNormalizado = yAudio/audioMax

    plt.figure("tempo")
    plt.plot(yAudioNormalizado)
    plt.grid()
    plt.title('Oi no tempo')


    #####################
    # Filtro
    #####################
  
    #####################
    # Aplica filtro no sinal
    #####################

    #####################
    # FFT Sinal filtrado
    #####################

    X, Y = calcFFT(yFiltrado, samplerate)
    plt.figure("Fourier Audio")
    plt.plot(X, np.abs(Y))
    plt.grid()
    plt.title('Oi Frequencia')

    #####################
    # Gera portadora
    #####################
    freqPortadora = 13000
    xPortadora, yPortadora = generateSin(freqPortadora, 1, samplesAudio/samplerate, samplerate)
    plt.figure("portadora")
    plt.title('Portadora')
    plt.plot(xPortadora[0:500], yPortadora[0:500])
    plt.grid()

    #####################
    # Gera sinal AM
    # AM-SC
    #####################
    yAM = yFiltrado * yPortadora
    plt.figure("AM")
    plt.title('AM')
    plt.plot(yAM[0:500])
    plt.grid()

    # Fourier mensagem
    XAM, YAM = calcFFT(yAM, samplerate)
    plt.figure("Fourier mensagem")
    plt.plot(XAM, np.abs(YAM))
    plt.grid()
    plt.title('msg Frequencia')

    #####################
    # Demodula sinal AM
    # AM-SC
    # via product detection e low pass filter
    # https://en.wikipedia.org/wiki/Product_detector
    #####################
    audioAM, audioAMFS = sf.read('oiModuladoAM.wav')
    yAMFile = audioAM[:,1]

    xPortadoraDemod, yPortadoraDemod = generateSin(freqPortadora, 1, len(yAMFile)/samplerate, samplerate)

    yDemod = yAMFile * yPortadoraDemod
    yDemodFiltrado  = signal.lfilter(taps, 1.0, yDemod)

    XAMDemod, YAMDemod = calcFFT(yDemod, samplerate)
    XAMDemodFiltrado, YAMDemodFiltrado = calcFFT(yDemodFiltrado, samplerate)
    plt.figure("Fourier mensagem demodulada")
    #plt.plot(XAMDemod, np.abs(YAMDemod))
    plt.plot(XAMDemodFiltrado, np.abs(YAMDemodFiltrado))
    plt.grid()
    plt.title('msg Frequencia')


    #####################
    # Reproduz audio
    #####################
    sd.play(yDemod, samplerate)

    #####################
    # Reproduz audio
    #####################
    sd.play(yDemodFiltrado, samplerate)

    ## Exibe gráficos
    plt.show()
    sd.wait()

    


if __name__ == "__main__":
    main()
