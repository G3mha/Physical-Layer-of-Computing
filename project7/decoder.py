from suaBibSignal import *
import peakutils # possible turn-arounds: ```from detect_peaks import *``` or ```import pickle```
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import time

print('Starting decoder\nGenerating base tones')
signal = signalMeu() # makes an instance of the class used to generate the signal
sd.default.samplerate = 1 # default sampling rate (Hz)
sd.default.channels = 2 # tipically the sound boards are 2 channeled (when recording, it will return two lists). If doenst work, try with 1
duration = 10 # a little longer than the time that the signal is being played
frequency_table = [[941, 1336],[697, 1209],[697, 1336],[697, 1477],[770, 1209],[770, 1336],[770, 1477],[852, 1209],[852, 1336],[852, 1477]] # list of corresponding frequencies for each number in DMTF table
sampling_rate = 44100 # true sampling rate (Hz)
samples_amount = duration * sampling_rate # number of samples to be recorded


time2prepare = 1 # time to prepare the recording
print(f'Starting recording in {time2prepare} seconds')
time.sleep(time2prepare)
print('Recording...')
audio = sd.rec(samples_amount, sampling_rate, channels=1) # records the audio
sd.wait() # waits for the recording to finish
print("...Recording finished")

y = audio[:, 0] # extracts the audio data from the audio variable

## Calcule e plote o Fourier do sinal audio. como saida tem-se a amplitude e as frequencias
signal.plotFFT(y, sampling_rate)
plt.xlim(0, 2000)
plt.show()


# use a funcao linspace e crie o vetor tempo. Um instante correspondente a cada amostra
# plot do áudio gravado (dados) vs tempo! Não plote todos os pontos, pois verá apenas uma mancha (freq altas) . 



xf, yf = signal.calcFFT(y, sampling_rate)
#agora, voce tem os picos da transformada, que te informam quais sao as frequencias mais presentes no sinal. Alguns dos picos devem ser correspondentes às frequencias do DTMF!
#Para descobrir a tecla pressionada, voce deve extrair os picos e compara-los à tabela DTMF
#Provavelmente, se tudo deu certo, 2 picos serao PRÓXIMOS aos valores da tabela. Os demais serão picos de ruídos.

# para extrair os picos, voce deve utilizar a funcao peakutils.indexes(,,)
# Essa funcao possui como argumentos dois parâmetros importantes: "thres" e "min_dist".
# "thres" determina a sensibilidade da funcao, ou seja, quao elevado tem que ser o valor do pico para de fato ser considerado um pico
#"min_dist" é relatico tolerancia. Ele determina quao próximos 2 picos identificados podem estar, ou seja, se a funcao indentificar um pico na posicao 200, por exemplo, só identificara outro a partir do 200+min_dis. Isso evita que varios picos sejam identificados em torno do 200, uma vez que todos sejam provavelmente resultado de pequenas variações de uma unica frequencia a ser identificada.   
# Comece com os valores:
index = peakutils.indexes(yf, thres=0.2, min_dist=150)
print("index de picos {}" .format(index)) #yf é o resultado da transformada de fourier
#printe os picos encontrados! 
print("frequencias de pico {}" .format(xf[index])) #xf é o vetor das frequencias


#encontre na tabela duas frequencias proximas às frequencias de pico encontradas e descubra qual foi a tecla
#print o valor tecla!!!
    




peak_frequencies = xf[index]

error_list = []
true_peak_frequencies = []

for peak_frequency in peak_frequencies:
    if peak_frequency < 1490 and peak_frequency > 680:
        true_peak_frequencies.append(peak_frequency)

for frequency_duo in frequency_table:
    error = abs(frequency_duo[0] - true_peak_frequencies[0]) + abs(frequency_duo[1] - true_peak_frequencies[1])
    error_list.append(error)
key_pressed = error_list.index(min(error_list))
print(f'Pressed key: {key_pressed}')
    

# freq_below1000 = []
# freq_above1000 = []
# for f in peak_frequencies:
#     if f > 1000:
#         freq_above1000.append(f)
#     else:
#         freq_below1000.append(f)

# possible_key1 = 0
# possible_key2 = 0

# current_error_below1000 = 1000
# current_error_above1000 = 1000

# for i in range(len(frequency_table)):
#     for f in freq_below1000:
#         error = abs(f - frequency_table[i][0])
#         if error < current_error_below1000:
#             curr_error_below = error
#             possible_key1 = i
#     for f in freq_above1000:
#         error = abs(f - frequency_table[i][1])
#         if error < current_error_above1000:
#             curr_error_above = error
#             possible_key2 = i
    


# if possible_key1 != possible_key2:
#     print('Not able to identify the pressed key. Please try again.')
# else: 
#     print(f'Pressed key: {possible_key1}')
