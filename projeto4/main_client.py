#####################################################
# Camada Física da Computação
# Enricco Gemha
# 15/09/2022
# Projeto 4
####################################################

from cgitb import reset
from itertools import count
from pyexpat.errors import messages
from timeit import repeat
from enlace import *
import time
import numpy as np
from utils import *

#   python -m serial.tools.list_ports (communication port label)

serial_name = "/dev/tty.usbmodem1411"
img = 'projeto4/img/batman.png'
msg_client = Message(img)
verifier = Verifier(from_server=True)


def main():
    try:
        msg_client.set_msg_type(1) # 1 = handshake
        msg_client.set_HEAD()
        pkg_handshake_client = msg_client.make_pkg()

        com1 = enlace(serial_name); com1.enable(); print("Abriu a comunicação")

        begin = False
        while not(begin):
            com1.rx.clearBuffer()

            com1.sendData(b'00'); time.sleep(.1) # sacrifice bit
            com1.sendData(pkg_handshake_client); time.sleep(.1) # handshake
            
            time.sleep(5)

            if com1.rx.getIsEmpty():
                continue

            handshake_from_server, _ = com1.getData(14)
            handshake_is_correct = verifier.verify_handshake(handshake_from_server)
            if handshake_is_correct:
                print("Handshake está correto."); begin = True

        counter = 1
        number_of_packages = msg_client.amount_of_packages
        while counter <= number_of_packages:
            msg_client.set_msg_type(3)
            msg_client.set_HEAD(current_pkg_number=counter)
            pkg_type3 = msg_client.make_pkg()
            com1.sendData(pkg_type3); time.sleep(.1)
            timer1 = Timer(5)
            timer2 = Timer(20)
            while True:
                pkg_type4 = [0]
                if not(com1.rx.getIsEmpty()):
                    pkg_type4, _ = com1.getData(14)
                pkg_is_correct = verifier.verify_pkg_type4(pkg_type4)
                if pkg_is_correct:
                    counter += 1
                    break
                if timer1.is_timeout():
                    com1.sendData(pkg_type3); time.sleep(.1)
                    timer1.reset()
                if timer2.is_timeout():
                    msg_client.set_msg_type(5)
                    msg_client.set_HEAD()
                    pkg_type5 = msg_client.make_pkg()
                    com1.sendData(pkg_type5); print("Timeout. Comunição encerrada"); com1.disable()
                pkg_type6 = [0]
                if not(com1.rx.getIsEmpty()):
                    pkg_type6, _ = com1.getData(14)
                if not(verifier.verify_pkg_type6(pkg_type6)):
                    continue
                counter = pkg_type6[6]
                msg_client.set_msg_type(3)
                msg_client.set_HEAD(current_pkg_number=counter)
                pkg_type3 = msg_client.make_pkg()
                com1.sendData(pkg_type3); time.sleep(.1)
                timer1.reset()
                timer2.reset()
    
        print('Transmissão bem sucedida'); com1.disable()

    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
