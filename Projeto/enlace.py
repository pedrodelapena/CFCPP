#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
# Prof. Rafael Corsi
#  Abril/2017
#  Camada de Enlace
####################################################

# Importa pacote de tempo
import time

import sys # da time out de um jeito estiloso

# Construct Struct
from construct import *
import hashlib

# Interface Física
from interfaceFisica import fisica

# enlace Tx e Rx
from enlaceRx import RX
from enlaceTx import TX

import math # necessario para divisão de pacotes



class enlace(object):
    """ This class implements methods to the interface between Enlace and Application
    """
    headSTART = 0xFF # 255 #super clever head start
    headStruct = Struct("start" / Int8ub,"size" / Int16ub,"SYN" / Int8ub,"ACK_NACK" / Int8ub,"P_size" / Int8ub,"P_total" / Int8ub )
    ackCode = 0x9d # 157
    nackCode = 0x0e # 14
    synCode = 0x01 # 1

    fakeAck = 0x00
    fakeSyn = 0x00

    maximum_Package = 2048 *8 # determina o tamanho maximo que um pacote pode ter (*8 pois precisa ser em bits)

    def __init__(self, name):
        """ Initializes the enlace class
        """
        self.fisica      = fisica(name)
        self.rx          = RX(self.fisica)
        self.tx          = TX(self.fisica)
        self.connected   = False
        self.end         = "s.t.o.p.".encode()

    def enable(self):
        """ Enable reception and transmission
        """
        self.fisica.open()
        self.rx.threadStart()
        self.tx.threadStart()

    def disable(self):
        """ Disable reception and transmission
        """
        self.rx.threadKill()
        self.tx.threadKill()
        time.sleep(1)
        self.fisica.close()

    def buildHead(self, dataLen):
        head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.fakeSyn, ACK_NACK = self.fakeAck,P_size = 0, P_total =0))
        return(head)

    def buildSync(self, dataLen = 0):
        head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.synCode, ACK_NACK = self.fakeAck,P_size = 0, P_total =0))
        return(head)

    def buildACK_NACK(self, dataLen = 0,deuCerto = False):
        if deuCerto == True:
            head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.synCode, ACK_NACK = self.ackCode,P_size = 0, P_total =0))
        if deuCerto == False:
            head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.synCode, ACK_NACK = self.nackCode,P_size = 0, P_total =0))
        return(head)

    def build_complete(self, dataLen,deuCerto = True,P_size,P_total):
        head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.synCode, ACK_NACK = self.ackCode,P_size = 0, P_total =0))


    def getheadStart(self,file):
        head = file[0:7]
        container = self.headStruct.parse(head)
        return container["start"]

    def getSize(self,file):
        head = file[0:7]
        container = self.headStruct.parse(head)
        return container["size"]

    def getSYN(self,file):
        head = file[0:7]
        container = self.headStruct.parse(head)
        return container["SYN"]

    def getACK_NACK(self,file):
        head = file[0:7]
        container = self.headStruct.parse(head)
        return container["ACK_NACK"]

    def getP_size_total(self,file):
        head = file[0:7]
        container = self.headStruct.parse(head)
        return (container["P_size"],container["P_total"])

    def Compare_number_package(self,file): # compara se todos os pacotes foram recebidos

       
        P_size,P_total = self.getP_size_total(file)

        print("Compare debug: ",P_size," ",P_total)

        if P_size = P_total :
        	return True
        else:
        	return False

    def DataSender(self,data):
    	"""
		#Exemplo basico
		
		n = 3 # tamanho maximo do pacote

		a = b"0123456789"

		quantidade_partes = math.ceil(len(a)/n) # acha a quantidade minima de partes que o pacote de ser dividido

		print(quantidade_partes)

		beginning = 0
		end = n

		Parte_atual = 0

		while Parte_atual < quantidade_partes: # roda a quantidade de vezes minima
		    print(a[beginning:end])
		    beginning += n
		    end += n
		    Parte_atual += 1

		"""

		n = self.maximum_Package # tamanho maximo do pacote, so mudei de nome

		quantidade_partes = math.ceil(len(data)/n) # acha a quantidade minima de partes que o pacote de ser dividido

		print("quantidade de partes necessarias : ",quantidade_partes)

		beginning = 0
		end = n
		Parte_atual = 1

		while Parte_atual <= quantidade_partes # roda a quantidade de vezes minima
		    #print(a[beginning:end])

		    head = self.build_complete(len(data),True,Parte_atual,quantidade_partes)
		    data = (head + data + self.end) # susbistituir todo esse bagulho pelo DataSender des daqui...
		    #print(data)
		    self.tx.sendBuffer(data)

            timeout = time.time()

		    while time.time() - timeout <= 3.0:
                ack_esperado = self.rx.getNData()
                if self.getACK_NACK(ack_esperado) == 157:
                    beginning += n
                    end += n
                    Parte_atual += 1

		    







    def handshake_server(self):
        while True:
            if self.rx.getBufferLen() > 4:
            	time_start_getData = time.time()
                data = self.rx.getNData() # receive syn
                if self.getSYN(data) == 1:
                    print("Syn recebido, send ack + syn")
                    
                    time.sleep(0.1)
                    self.tx.sendBuffer(self.buildACK_NACK(deuCerto = True) + self.end) #ack + syn
                    self.rx.clearBuffer()

                    data = self.rx.getNData() #receive ack
                    if self.getACK_NACK(data) == 157:
                        print("handshake completo")
                        break

    ################################
    # Application  interface       #
    ################################
    def sendData(self, txLen, data):
        """ Send data over the enlace interface
        """
        sync = (self.buildSync() + self.end)
        head = self.buildHead(txLen)

        time_inicio = time.time()

        while True:
            
            time.sleep(1)
            self.tx.sendBuffer(sync)
            self.rx.clearBuffer()
            print("Mandei o Sync \:3")

            time_now = time.time()
            if (time_now - time_inicio) < 30.0:

                ack_syn = self.rx.getNData()
                if self.getACK_NACK(ack_syn) == 157 and self.getSYN(ack_syn) == 1: 
                    print("Mandei o ACK \:3")
                    time.sleep(1)
                    self.tx.sendBuffer(self.buildACK_NACK(deuCerto=True) + self.end)
                    break

            elif (time_now - time_inicio) > 30.0:
                sys.exit()

        time.sleep(1)


        data = (head + data + self.end) # susbistituir todo esse bagulho pelo DataSender des daqui...
        print(data)
        self.tx.sendBuffer(data) 

        time_for_check = time.time()

        while time_for_check < 1.0: #criar um novo jeito para mexer com os pacotes corrompidos
            ack_syn = self.rx.getNData()
            if self.getACK_NACK(ack_syn) == 14:
                print("pacote corrompido!")
                self.tx.sendBuffer(data)
                time_for_check = time.time() #...até aqui





    def getData(self):
        """ Get n data over the enlace interface
        Return the byte array and the size of the buffer
        """

        self.handshake_server()


        self.rx.clearBuffer()

        Complete_package = b""

        Current_P_size = 1

        while True: #pega um pacote
            data = self.rx.getNData()
            self.rx.clearBuffer()
            if self.getheadStart(data)==255: # se achar o head do pacote
            	payload = self.openPackage(data)

            	P_size = getP_size_total(data)

            	print("P_size,Current_P_size : ",P_size," ",Current_P_size)

            	if P_size = Current_P_size:
            		Complete_package += payload

            		self.tx.sendBuffer(self.buildACK_NACK(deuCerto = True) + self.end)
            		Current_P_size += 1


            	if Compare_number_package(data):
            		break

        print("Meu debug: "+str(data))
        data, head = self.openPackage(data)

        """

        while True: # checa se os sizes batem
            if self.getSize(head) != len(data) :
                print("dataLen:",dataLen,"head size",self.getSize(head))
                self.tx.sendBuffer(self.buildACK_NACK(deuCerto = False) + self.end)
                time.sleep(0.2)

                while True: #pega a data novamente
                    data = self.rx.getNData()
                    #self.rx.clearBuffer()
                    if self.getheadStart(data)==255:
                        break

                print("Meu debug: "+str(data))
                data, head = self.openPackage(data)

            else:
                break
        """

        print("tempo de trasmição: ",time_start_getData - time.time())
        return(Complete_package, len(Complete_package))

    def addHead(self, txLen, txBuffer):
        return (self.buildHead(txLen) + txBuffer)

    def decrypHead(self, head):
        return (struct.unpack(self.headStruct, head))

    def openPackage(self,file):

    	head = file[0:7]
    	file = file[7:-8]

    	return(file,head)

