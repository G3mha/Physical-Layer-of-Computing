#####################################################
# Camada Física da Computação
# Enricco Gemha
# 15/09/2022
# Projeto 4
####################################################


from itertools import count
from enlace import *
from utils import *
import time
import numpy as np

#   python -m serial.tools.list_ports (communication port label)

serial_name = "/dev/tty.usbmodem1411"
msg_server = Message('no_img')
verifier = Verifier(from_server=False)


def main():
    try:
        msg_server.set_msg_type(2)
        msg_server.set_HEAD()
        pkg_handshake_from_server = msg_server.make_pkg()

        com1 = enlace(serial_name); com1.enable(); print("Abriu a comunicação")
        rxBuffer, _ = com1.getData(1); com1.rx.clearBuffer(); time.sleep(.1)
        print('1 byte de sacrifício recebido. Limpou o buffer')

        idle = True
        while idle:
            if not(com1.rx.getIsEmpty()):
                handshake_from_client, _ = com1.getData(14)
                handshake_is_correct = verifier.verify_handshake(handshake_from_client)
                if handshake_is_correct:
                    print("Handshake está correto."); idle = False
            time.sleep(1)
        com1.sendData(pkg_handshake_from_server); time.sleep(.1)
        
        img_received = b''
        
        counter = 1
        number_of_packages = handshake_from_client[3]
        while counter <= number_of_packages:
            timer1 = Timer(2)
            timer2 = Timer(20)
            while True:
                pkg_type3 = [0]
                if not(com1.rx.getIsEmpty()):
                    pkg_type3, _ = com1.getData(14)
                pkg_is_type3 = verifier.verify_pkg_type3(pkg_type3)
                if not(pkg_is_type3):
                    time.sleep(1)
                    if timer2.is_timeout():
                        msg_server.set_msg_type(5)
                        msg_server.set_HEAD()
                        pkg_type5 = msg_server.make_pkg()
                        com1.sendData(pkg_type5); time.sleep(.1)
                        print('Comunicação encerrada'); idle = True; com1.disable()
                    if timer1.is_timeout():
                        timer1.reset()
                    continue
                if pkg_is_type3:
                    eop_is_correct = verifier.verify_eop(pkg_type3)
                    order_is_correct = (counter == pkg_type3[4])
                    if eop_is_correct and order_is_correct:
                        msg_server.set_msg_type(4)
                        msg_server.set_last_pkg_sucesfully_received(counter)
                        msg_server.set_HEAD()
                        pkg_type4 = msg_server.make_pkg()
                        com1.sendData(pkg_type4); time.sleep(.1)
                        counter += 1
                        img_received += payload_client # pegando e guardando as informações do payload
                        # colocar aqui o payload na lista de payloads
                        break
                    if not(eop_is_correct) or not(order_is_correct):
                        msg_server.set_msg_type(6)
                        msg_server.set_HEAD(expected_pkg_number=counter)
                        pkg_type6 = msg_server.make_pkg()
                        com1.sendData(pkg_type6); time.sleep(.1)
                        break


        print('Transmissão bem sucedida'); com1.disable()




        HEAD_handshake_client, _ = com1.getData(10); time.sleep(.1)
        is_handshake_correct = verifica_handshake(HEAD_handshake_client[0:2], False)
        total_of_packages = HEAD_handshake_client[4]

        if is_handshake_correct:
            payload_size = int(HEAD_handshake_client[2])
            resto_of_handshake_client, _ = com1.getData(payload_size+4) ; time.sleep(.1)
            handshake_client = HEAD_handshake_client + resto_of_handshake_client
            eop_verificado = verifica_eop(handshake_client, HEAD_handshake_client)
            if not eop_verificado:
                return
            handshake_server = np.asarray(HEAD_handshake_server + EOP)
            com1.sendData(handshake_server); time.sleep(.1)
            print('Resposta do handshake enviado')

        img_received = b''
        package_before, packages_received = 1, 0
        while True:
            HEAD_client, _ = com1.getData(10); time.sleep(0.5)
            payload_size, current_package, _ = retirando_informacoes_do_head(HEAD_client)

            if current_package != package_before:
                print(current_package, package_before)
                print('Erro na ordem dos pacotes recebidos.')
                HEAD_server = bytes([6,0,0,0,0,0,0,0,0,0])
                com1.sendData(HEAD_server+EOP); com1.disable(); return
            else:
                HEAD_server = bytes([7,0,0,0,0,0,0,0,0,0])
                com1.sendData(HEAD_server+EOP); time.sleep(0.5)

            packages_received += 1
            package_before = current_package

            rest_of_package_client, _ = com1.getData(payload_size + 4); time.sleep(0.2)
            package_client = HEAD_client + rest_of_package_client
            
            HEAD_client, payload_client, EOP_client = tratar_pacote_recebido(package_client) #separando head, payloas e eop.
            img_received += payload_client # pegando e guardando as informações do payload
            
            is_eop_correct = verifica_eop(package_client, HEAD_client) #verificando se eop está no lugar certo
            if not is_eop_correct:
                com1.disable(); return
                # TODO placeholder para implementacao de reenvio 
                # Aqui quando der erro no eop deve mostrar que ou o EOP esta errado ou o tamanho do payload informado est[a incorreto]]
                
            if packages_received == total_of_packages:
                break
            if packages_received != total_of_packages:
                package_before += 1

        final_HEAD_client = bytes([1,0,0,0,0,0,0,0,0,0])
        if packages_received != total_of_packages:
            print('Número de pacotes recebidos diferente do total enviado')
        else:
            final_HEAD_client = bytes([1,0,0,0,0,1,0,0,0,0])
            print('Transmissão foi um sucesso')

        final_package = final_HEAD_client + EOP
        com1.sendData(final_package); time.sleep(.2)
        img_received_name = 'projeto3/img/recebido.PNG'
        print("Salvando dados no arquivo")
        f = open(img_received_name, 'wb')
        f.write(img_received)
        f.close() # fecha o arquivo de imagem

        print("-------------------------\nComunicação encerrada\n-------------------------"); com1.disable()


    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()


    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
