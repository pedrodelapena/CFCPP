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

import crcmod



class enlace(object):
    """ This class implements methods to the interface between Enlace and Application
    """
    headSTART = 0xFF # 255 #super clever head start
    headStruct = Struct("start" / Int8ub,"size" / Int16ub,"SYN" / Int8ub,"ACK_NACK" / Int8ub,"P_size" / Int8ub,"P_total" / Int8ub,"CheckSum" / Int16ub,"CheckSum_head" / Int16ub )
    ackCode = 0x9d # 157
    nackCode = 0x0e # 14
    synCode = 0x01 # 1

    fakeAck = 0x00
    fakeSyn = 0x00

    maximum_Package = 2048 # determina o tamanho maximo que um pacote pode ter (*8 pois precisa ser em bits)

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
        head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.fakeSyn, ACK_NACK = self.fakeAck,P_size = 0, P_total =0,CheckSum = 0, CheckSum_head =0))
        return(head)

    def buildSync(self, dataLen = 0):
        head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.synCode, ACK_NACK = self.fakeAck,P_size = 0, P_total =0,CheckSum = 0, CheckSum_head =0))
        return(head)

    def buildACK_NACK(self, dataLen = 0,deuCerto = False):
        if deuCerto == True:
            head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.synCode, ACK_NACK = self.ackCode,P_size = 0, P_total =0,CheckSum = 0, CheckSum_head =0))
        if deuCerto == False:
            head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.synCode, ACK_NACK = self.nackCode,P_size = 0, P_total =0,CheckSum = 0, CheckSum_head =0))
        return(head)

    def build_complete(self, dataLen,deuCerto,payload_len,total_payload_len,CheckSum_payload,CheckSum_head):
        head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.synCode, ACK_NACK = self.ackCode,P_size = payload_len, P_total = total_payload_len,CheckSum = CheckSum_payload, CheckSum_head =CheckSum_head))
        return(head)

    def getheadStart(self,file):
        head = file[0:11]
        container = self.headStruct.parse(head)
        return container["start"]

    def getSize(self,file):
        head = file[0:11]
        container = self.headStruct.parse(head)
        return container["size"]

    def getSYN(self,file):
        head = file[0:11]
        container = self.headStruct.parse(head)
        return container["SYN"]

    def getACK_NACK(self,file):
        head = file[0:11]
        container = self.headStruct.parse(head)
        return container["ACK_NACK"]

    def getP_size_total(self,file):
        head = file[0:11]
        container = self.headStruct.parse(head)
        return (container["P_size"],container["P_total"])


    def CRC(self,data):
        # usando crc-16-IBM aka CRC-16
        crc16 = crcmod.predefined.mkCrcFun("crc-16")

        CRC = (crc16(data))
        print("CRC: ",CRC)
        return CRC

    def get_CRC(self,file):
        head = file[0:11]
        container = self.headStruct.parse(head)
        return (container["CheckSum"],container["CheckSum_head"])

    def compare_CRC(self,file): # função que retorna True Se o CRChead e CRCpayload estiverem certos
        crc16 = crcmod.predefined.mkCrcFun("crc-16")
        CheckSum,CheckSum_head = self.get_CRC(file)
        half_head = file[0:7] # parte do head sem CRC

        data, useless_trash = self.openPackage(file)

        if CheckSum == crc16(data) and CheckSum_head == crc16(half_head):
            return True
        else:
            return False

    def Compare_number_package(self,file): # compara se todos os pacotes foram recebidos

       
        P_size,P_total = self.getP_size_total(file)

        print("Compare debug: ",P_size," ",P_total)

        if P_size == P_total :
            return True
        else:
            return False

    def DataSender(self,data):

        n = self.maximum_Package # tamanho maximo do pacote, so mudei de nome

        quantidade_partes = math.ceil(len(data)/n) # acha a quantidade minima de partes que o pacote de ser dividido

        print("quantidade de partes necessarias : ",quantidade_partes)
        print("bytes em cada pacote:",quantidade_partes,"*",n," + ",len(data)%n)

        beginning = 0
        end = n
        Parte_atual = 1

        while Parte_atual <= quantidade_partes: # roda a quantidade de vezes minima
            #print(a[beginning:end])

            temp_head = self.build_complete(len(data),True,Parte_atual,quantidade_partes,0,0)
            head_crc = self.CRC(temp_head[0:7]) # a parte do head sem o CRC
            payload_crc = self.CRC(data)

            head = self.build_complete(len(data),True,Parte_atual,quantidade_partes,payload_crc,head_crc)

            data = (head + data + self.end)
            print("Parte_atual,quantidade_partes",Parte_atual,quantidade_partes)
            self.tx.sendBuffer(data)

            timeout = time.time()

            while time.time() - timeout <= 3.0:
                ack_esperado = self.rx.getNData()
                if self.getheadStart(ack_esperado)==255:
                    if self.getACK_NACK(ack_esperado) == 157:
                        beginning += n
                        end += n
                        Parte_atual += 1
                        break
                    elif self.getACK_NACK(ack_esperado) == 14:
                        break

                time.sleep(0.05)

		    



    def handshake_server(self):
        while True:
            if self.rx.getBufferLen() > 4:
                time_start_getData = time.time()
                data = self.rx.getNData() # receive syn
                if self.getSYN(data) == 1:
                    print("Syn recebido, send ack + syn")
                    
                    time.sleep(0.1)
                    ack_nack = self.buildACK_NACK(deuCerto = True)
                    self.tx.sendBuffer(ack_nack + self.end) #ack + syn
                    print(self.getACK_NACK(ack_nack))


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
                if self.getheadStart(data)==255:
                    if self.getACK_NACK(ack_syn) == 157 and self.getSYN(ack_syn) == 1: 
                        print("Mandei o ACK \:3")
                        time.sleep(1)
                        self.tx.sendBuffer(self.buildACK_NACK(deuCerto=True) + self.end)
                        break

            elif (time_now - time_inicio) > 30.0:
                sys.exit()

        time.sleep(1)

        self.DataSender(data)


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
                payload, trash = self.openPackage(data)

                P_size,P_total = self.getP_size_total(data)

                print("P_size,Current_P_size : ",P_size," ",Current_P_size)


                if P_size == Current_P_size and self.compare_CRC(data):
                    print("Payload : ",type(payload))


                    Complete_package += payload

                    head = self.buildACK_NACK(deuCerto = True)
                    print("mandei ack",head)
                    self.tx.sendBuffer(head + self.end)


                    Current_P_size += 1

                if self.compare_CRC(data) == False:

                    head = self.buildACK_NACK(deuCerto = False)
                    print("A casa caiu, arquivo corrompido, mandado nack")
                    self.tx.sendBuffer(head + self.end)



                if P_size == P_total:
                    break

        #print("Meu debug: "+str(Complete_package))
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

        #print("tempo de trasmição: ",time_start_getData - time.time())

        return(Complete_package, len(Complete_package))

    def addHead(self, txLen, txBuffer):
        return (self.buildHead(txLen) + txBuffer)

    def decrypHead(self, head):
        return (struct.unpack(self.headStruct, head))

    def openPackage(self,file):

    	head = file[0:11]
    	file = file[11:-8]

    	return(file,head)

