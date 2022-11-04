#     signal = signalMeu() 

#     freqs = {
#         0: [941, 1336],
#         1: [697, 1209],
#         2: [697, 1336],
#         3: [697, 1477],
#         4: [770, 1209],
#         5: [770, 1336],
#         6: [770, 1477],
#         7: [852, 1209],
#         8: [852, 1336],
#         9: [852, 1477],
#     }
       
    # #voce importou a bilioteca sounddevice como, por exemplo, sd. entao
    # # os seguintes parametros devem ser setados:
    # sd.default.samplerate = 1 #taxa de amostragem
    # sd.default.channels = 2 #numCanais # o numero de canais, tipicamente são 2. Placas com dois canais. Se ocorrer problemas pode tentar com 1. No caso de 2 canais, ao gravar um audio, terá duas listas
    # duration = 8 # #tempo em segundos que ira aquisitar o sinal acustico captado pelo mic
    
    # freqDeAmostragem = 44100
    # numAmostras = duration * freqDeAmostragem

    #calcule o numero de amostras "numAmostras" que serao feitas (numero de aquisicoes) durante a gracação. Para esse cálculo você deverá utilizar a taxa de amostragem e o tempo de gravação

    #faca um print na tela dizendo que a captacao comecará em n segundos. e entao 
    #use um time.sleep para a espera
   
    #Ao seguir, faca um print informando que a gravacao foi inicializada

    #para gravar, utilize
    audio = sd.rec(int(numAmostras), freqDeAmostragem, channels=1)
    sd.wait()
    print("...     FIM")
    y = audio[:, 0]
    # print(audio[:,0])


    #analise sua variavel "audio". pode ser um vetor com 1 ou 2 colunas, lista, isso dependerá so seu sistema, drivers etc...
    #extraia a parte que interessa da gravação (as amostras) gravando em uma variável "dados". Isso porque a variável audio pode conter dois canais e outas informações). 
    
    # use a funcao linspace e crie o vetor tempo. Um instante correspondente a cada amostra!
  
    # plot do áudio gravado (dados) vs tempo! Não plote todos os pontos, pois verá apenas uma mancha (freq altas) . 
       
    ## Calcule e plote o Fourier do sinal audio. como saida tem-se a amplitude e as frequencias
    xf, yf = signal.calcFFT(y, freqDeAmostragem)

    signal.plotFFT(y, freqDeAmostragem)
    plt.xlim(0, 2500)
    plt.show()

    
    #agora, voce tem os picos da transformada, que te informam quais sao as frequencias mais presentes no sinal. Alguns dos picos devem ser correspondentes às frequencias do DTMF!
    #Para descobrir a tecla pressionada, voce deve extrair os picos e compara-los à tabela DTMF
    #Provavelmente, se tudo deu certo, 2 picos serao PRÓXIMOS aos valores da tabela. Os demais serão picos de ruídos.

    # para extrair os picos, voce deve utilizar a funcao peakutils.indexes(,,)
    # Essa funcao possui como argumentos dois parâmetros importantes: "thres" e "min_dist".
    # "thres" determina a sensibilidade da funcao, ou seja, quao elevado tem que ser o valor do pico para de fato ser considerado um pico
    #"min_dist" é relatico tolerancia. Ele determina quao próximos 2 picos identificados podem estar, ou seja, se a funcao indentificar um pico na posicao 200, por exemplo, só identificara outro a partir do 200+min_dis. Isso evita que varios picos sejam identificados em torno do 200, uma vez que todos sejam provavelmente resultado de pequenas variações de uma unica frequencia a ser identificada.   
    # Comece com os valores:
    index = peakutils.indexes(yf, thres=0.2, min_dist=150)
    #print("index de picos {}" .format(index)) #yf é o resultado da transformada de fourier
    print("frequencias de pico {}" .format(xf[index])) #xf é o vetor de frequencias

    

    freqs_possibles = xf[index]

    freq_below_1000 = [f for f in freqs_possibles if f < 1000]
    freq_above_1000 = [f for f in freqs_possibles if f > 1000]

    curr_error_below = 10000
    key1 = None
    for i in range(10):
        for f in freq_below_1000:
            error = abs(f - freqs[i][0])
            if error < curr_error_below:
                curr_error_below = error
                freq1 = f
                key1 = i
    
    # please copilot repeat my code
    curr_error_above = 10000
    key2 = None
    for i in range(10):
        for f in freq_above_1000:
            error = abs(f - freqs[i][1])
            if error < curr_error_above:
                curr_error_above = error
                freq2 = f
                key2 = i
    


    if key1 != key2:
        print("Não foi possível identificar a tecla (Erro absoluto muito alto)")
    else: 
        print("Tecla pressionada: {}" .format(key1))


    #printe os picos encontrados! 
    # Aqui você deverá tomar o seguinte cuidado: A funcao  peakutils.indexes retorna as POSICOES dos picos. Não os valores das frequências onde ocorrem! Pense a respeito
    
    #encontre na tabela duas frequencias proximas às frequencias de pico encontradas e descubra qual foi a tecla
    #print o valor tecla!!!
    #Se acertou, parabens! Voce construiu um sistema DTMF

    #Você pode tentar também identificar a tecla de um telefone real! Basta gravar o som emitido pelo seu celular ao pressionar uma tecla. 


      
    ## Exiba gráficos do fourier do som gravados 
    plt.show()