import time
import numpy as np
from math import ceil


class Message():
    def __init__(self, img):
        self.EOP = b'\xAA\xBB\xCC\xDD'
        if img != 'no_img':
            self.img = img
            self.make_list_payload()

    def make_list_payload(self):
        img_bin = open(self.img,'rb').read()
        img_size = len(img_bin)
        pkgs = ceil(img_size/114)
        payloads = []
        for i in range(pkgs):
            if i == (pkgs-1):
                payload = img_bin[114*i:img_size]
                print('tamanho do ultimo payload ' , len(payload))
            else:
                payload = img_bin[114*i:(i+1)*114]
                print('tamanho dos payloads intermediarios : ',len(payload))
            payloads.append(payload)
        self.list_payload = payloads
        self.amount_of_pkgs = len(payloads)
        self.current_pkg_number = 0

    def set_msg_type(self, msg_type):
        self.msg_type = msg_type

    def set_last_pkg_sucesfully_received(self, last_pkg_sucesfully_received):
        self.last_pkg_sucesfully_received = last_pkg_sucesfully_received

    def set_HEAD(self, current_pkg_number=0, expected_pkg_number=0):
        self.current_pkg_number = current_pkg_number
        self.current_payload_size = self.list_payload[current_pkg_number-1]

        if self.msg_type == 1: # handshake from client to server (question)
            server_ID = 9 # server ID attached to message
            list_HEAD = [self.msg_type,0,0,self.amount_of_pkgs,0,server_ID,0,0,0,0]
        
        if self.msg_type == 2: # handshake from server to client (answer)
            list_HEAD = [self.msg_type,0,0,0,0,0,0,0,0,0]

        if self.msg_type == 3: # data from client to server (payload not 0)
            list_HEAD = [self.msg_type,0,0,self.amount_of_pkgs,current_pkg_number,self.current_payload_size,0,0,0,0]

        if self.msg_type == 4: # payload check from server to client (sucessfully received)
            list_HEAD = [self.msg_type,0,0,0,0,0,0,self.last_pkg_sucesfully_received,0,0]

        if self.msg_type == 5: # timeout connection from any to other (end communication)
            list_HEAD = [self.msg_type,0,0,0,0,0,0,0,0,0]

        if self.msg_type == 6: # error on package from server to client (missing bytes or incorrect format or unexpected package)
            list_HEAD = [self.msg_type,0,0,0,0,0,expected_pkg_number,0,0,0]

        self.HEAD = bytes(list_HEAD)

    def make_pkg(self):
        payload = self.list_payload[self.current_pkg_number]
        pkg = self.HEAD + payload + self.EOP
        return np.asarray(pkg)
    
class Verifier():
    def __init__(self, from_server):
        self.from_server = from_server

    def verify_handshake(self, handshake):
        if self.from_server:
            expected = bytes([2])
            received = handshake[0]
            if received == expected:
                return True
            return False

        else: # from client
            expected = [bytes([1]), bytes([9])]
            received = [handshake[0], handshake[5]]
            if received == expected:
                return True
            return False
    
    def verify_EOP(self, pkg):
        if pkg[-4:] == self.EOP:
            return True
        return False

    def verify_pkg_type3(self, pkg_type3):
        expected = bytes([3])
        received = pkg_type3[0]
        if received == expected:
            return True
        return False
    
    def verify_pkg_type4(self, pkg_type4):
        expected = bytes([4])
        received = pkg_type4[0]
        if received == expected:
            return True
        return False

    def verify_pkg_type6(self, pkg_type6):
        expected = bytes([6])
        received = pkg_type6[0]
        if received == expected:
            return True
        return False


class Timer():
    def __init__(self, timeout):
        self.timeout = timeout
        self.start_time = time.time()

    def is_timeout(self):
        return (time.time() - self.start_time) > self.timeout

    def reset(self):
        self.start_time = time.time()






def verifica_ordem(recebido, numero_do_pacote_atual):
    """
    Como combinado o byte que diz o número do pacote é o de número 4 do head ,
    função que será utilizada pelo server
    """
    head = recebido[0:11]
    numero_do_pacote = head[3]
    if numero_do_pacote == numero_do_pacote_atual:
        return True
    return False


def reagrupamento(lista_dos_payloads,tamanho_total_da_info, numero_de_pacotes_recebidos):
    """
    Nessa função iremos juntar os payloads dos pacotes recebidos e verificar se o número de pacotes recebidos foi correto 
    """
    info_total = ''
    for payload in lista_dos_payloads:
        info_total += payload
    
    if numero_de_pacotes_recebidos == tamanho_total_da_info:
        return True
    else:
        return False
        
def tratar_pacote_recebido(pacote):
    tamanho_pacote = len(pacote)
    head = pacote[0:10]

    tamanho = head[2]
    payload = pacote[10:10+tamanho]

    eop = pacote[10+tamanho:len(pacote)]

    return head,payload,eop
    

def retirando_informacoes_do_head(head):
    tamanho_do_payload = head[2]
    numero_do_pacote = head[3]
    numero_total_de_pacotes = head[4]
    return tamanho_do_payload,numero_do_pacote, numero_total_de_pacotes
