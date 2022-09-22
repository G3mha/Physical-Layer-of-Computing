import time
import numpy as np
from math import ceil


class Message():
    def __init__(self, img):
        self.EOP = b'\xAA\xBB\xCC\xDD'
        self.make_list_payload(img)

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

    def set_msg_type(self, msg_type):
        self.msg_type = msg_type

    def set_last_pkg_sucesfully_received(self, last_pkg_sucesfully_received):
        self.last_pkg_sucesfully_received = last_pkg_sucesfully_received

    def set_HEAD(self, current_pkg_number=0, current_payload_size=0, expected_pkg_number=0):
        self.current_pkg_number = current_pkg_number

        if self.msg_type == 1: # handshake from client to server (question)
            server_ID = 9 # server ID attached to message
            list_HEAD = [self.msg_type,0,0,self.amount_of_pkgs,0,server_ID,0,0,0,0]
        
        if self.msg_type == 2: # handshake from server to client (answer)
            list_HEAD = [self.msg_type,0,0,0,0,0,0,0,0,0]

        if self.msg_type == 3: # data from client to server (payload not 0)
            list_HEAD = [self.msg_type,0,0,self.amount_of_pkgs,current_pkg_number,current_payload_size,0,0,0,0]

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

class Timer():
    def __init__(self, timeout):
        self.timeout = timeout
        self.start_time = time.time()

    def is_timeout(self):
        return (time.time() - self.start_time) >= self.timeout


def verifica_handshake(head, is_server):
    """
    Função que verifica se o handshake é a resposta esperada (SIM)
    """
    handshake = head[:2] # primeiro e segundo bytes do head
    delta_t = 0
    conferencia = bytes([5,1])
    if not is_server:
        conferencia = bytes([4,0])
    while delta_t <= 5: # loop para gerar o timeout
        tempo_atual = float(time.time())
        if handshake == conferencia: # 5 é a mensagem de handshake e 1 é a resposta positiva
            print('Handshake realizado com sucesso')
            return True
        delta_t = atualiza_tempo(tempo_atual)
    return False

def verifica_eop(pacote, head):
    """
    Função que verifica se o payload é o mesmo que o esperado e se o pacote está correto
    """
    # head = pacote[:10]
    tamanho = head[2]
    eop = pacote[10+tamanho:]
    if eop == b'\xAA\xAA\xAA\xAA':
        print('Payload recebido integramente. Esperando novo pacote')
        return True
    print('Erro no EOP enviado. Tente novamente.')
    return False

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
