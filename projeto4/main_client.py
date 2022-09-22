#####################################################
# Camada Física da Computação
# Enricco Gemha
# 15/09/2022
# Projeto 4
####################################################

from pyexpat.errors import messages
from timeit import repeat
from enlace import *
import time
import numpy as np
from utils import *

#   python -m serial.tools.list_ports (communication port label)

serial_name = "/dev/tty.usbmodem1411"
img = 'projeto4/img/batman.png'


def main():
    try:
        messages_client = Message(img)
        messages_client.set_msg_type(1) # 1 = handshake
        messages_client.set_HEAD()
        handshake_client = messages_client.make_pkg()
        
        com1 = enlace(serial_name); com1.enable(); print("Abriu a comunicação")
        
        com1.sendData(b'00'); time.sleep(.1) # sacrifice bit
        com1.sendData(handshake_client); time.sleep(.1)
        try_connection = 'S'

        start_sending_pkgs = False
        while start_sending_pkgs == False:
            com1.rx.clearBuffer()
            timer = time.time()
            while com1.rx.getIsEmpty() and (atualiza_tempo(timer) < 5):
                pass
            if com1.rx.getIsEmpty():
                try_connection = str(input('Servidor inativo. Tentar novamente? S/N: '))
                if try_connection == 'S':
                    com1.sendData(b'00'); time.sleep(.1) # bit de sacrificio
                    com1.sendData(handshake_client); time.sleep(.1)
                if try_connection == 'N':
                    print('Servidor inativo. Tente novamente mais tarde.'); com1.disable(); return
            else:
                handshake_server, _ = com1.getData(14)
                is_handshake_correct = verifica_handshake(handshake_server, True)
                if not is_handshake_correct:
                    print('Handshake diferente do esperado. Tente novamente mais tarde.'); com1.disable(); return
                if is_handshake_correct:
                    print("Handshake vindo do server está correto."); start_sending_pkgs = True


        current_package = 1
        for payload in payloads_list: 
            HEAD_content_client = bytes([3,0,len(payload),current_package,len(payloads_list),0,0,0,0,0]) 
            package = HEAD_content_client + payload + EOP
            com1.sendData(np.asarray(package))
            current_package += 1
            
            feedback_to_client, _ = com1.getData(1); time.sleep(.1)
            if feedback_to_client == 6:
                print(f'Tamanho do payload incorreto no pacote {current_package}. Reenvie o pacote.'); com1.disable(); return
                # implementar no proximo projeto
            if feedback_to_client == 7:
                print(f'Pacote {current_package} enviado com sucesso.')
            com1.rx.clearBuffer(); time.sleep(.1)

        HEAD_final_server, _ = com1.getData(10) # Recebendo o HEAD do server
        is_transmission_correct = (HEAD_final_server[5] == 1)
        EOP_final_server, _ = com1.getData(4) # Recebendo o EOP do server
        package_final_server = HEAD_final_server + EOP_final_server
        is_eop_correct = verifica_eop(package_final_server, HEAD_final_server)

        if not is_transmission_correct:
            print('Erro no envio dos pacotes. Tente novamente.')
        if is_transmission_correct and is_eop_correct:
            print('Transmissão bem sucedida')
    
        print("-------------------------\nComunicação encerrada\n-------------------------"); com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
