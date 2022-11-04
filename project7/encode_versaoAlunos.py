
#importe as bibliotecas
from suaBibSignal import *
import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt

import math
import time
from suaBibSignal import *
import sys

#funções a serem utilizadas
def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)


def main():
    #********************************************instruções*********************************************** 
    # seu objetivo aqui é gerar duas senoides. Cada uma com frequencia corresposndente à tecla pressionada
    # então inicialmente peça ao usuário para digitar uma tecla do teclado numérico DTMF
    # agora, voce tem que gerar, por alguns segundos, suficiente para a outra aplicação gravar o audio, duas senoides com as frequencias corresposndentes à tecla pressionada, segundo a tabela DTMF
    # Essas senoides tem que ter taxa de amostragem de 44100 amostras por segundo, entao voce tera que gerar uma lista de tempo correspondente a isso e entao gerar as senoides
    # Lembre-se que a senoide pode ser construída com A*sin(2*pi*f*t)
    # O tamanho da lista tempo estará associada à duração do som. A intensidade é controlada pela constante A (amplitude da senoide). Construa com amplitude 1.
    # Some as senoides. A soma será o sinal a ser emitido.
    # Utilize a funcao da biblioteca sounddevice para reproduzir o som. Entenda seus argumento.
    # Grave o som com seu celular ou qualquer outro microfone. Cuidado, algumas placas de som não gravam sons gerados por elas mesmas. (Isso evita microfonia).
    
    # construa o gráfico do sinal emitido e o gráfico da transformada de Fourier. Cuidado. Como as frequencias sao relativamente altas, voce deve plotar apenas alguns pontos (alguns periodos) para conseguirmos ver o sinal
    
    NUM = int(input("Type the number you want to dial, from 0 to 9: "))
    sampling_rate = 44100 # signal processing (discrete)
    signal = signalMeu() # makes an instance of the class used to generate the signal
    n_frequencies = [[941, 1336],[697, 1209],[697, 1336],[697, 1477],[770, 1209],[770, 1336],[770, 1477],[852, 1209],[852, 1336],[852, 1477]] # list of corresponding frequencies for each number
    period = 1/sampling_rate # period of the signal
    amplitude = 1 # amplitude of the signal
    duration = 5 # duration of the signal
    
    t_range = np.arange(0, 3, period)
    f, f_line = n_frequencies[NUM][0], n_frequencies[NUM][1]
    tone = []

    for t in t_range:
        # f(t) = A * sin(wt)
        tone.append((amplitude * math.sin(2 * np.pi * f * t)) + (amplitude * math.sin(2 * np.pi * f_line * t))) # generates the sine wave

    print("Inicializando encoder")
    print("Aguardando usuário")
    print("Gerando Tons base")
    print("Executando as senoides (emitindo o som)")
    print("Gerando Tom referente ao símbolo : {}".format(NUM))
    
    sd.play(tone, sampling_rate) # plays the signal
    sd.wait() # waits for the end of the audio

    signal.plotFFT(tone, sampling_rate)
    plt.xlim(600, 1700)
    plt.show()

    plt.plot(t_range, tone)
    plt.xlim(0, 0.01)
    plt.show()



if __name__ == "__main__":
    main()
