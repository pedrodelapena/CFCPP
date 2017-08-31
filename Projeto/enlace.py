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



class enlace(object):
    """ This class implements methods to the interface between Enlace and Application
    """
    headSTART = 0xFF # 255 #super clever head start
    headStruct = Struct("start" / Int8ub,"size" / Int16ub,"SYN" / Int8ub,"ACK_NACK" / Int8ub )
    ackCode = 0x9d # 157
    nackCode = 0x0e # 14
    synCode = 0x01 # 1

    fakeAck = 0x00
    fakeSyn = 0x00

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
        head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.fakeSyn, ACK_NACK = self.fakeAck))
        return(head)

    def buildSync(self, dataLen = 0):
        head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.synCode, ACK_NACK = self.fakeAck))
        return(head)

    def buildACK_NACK(self, dataLen = 0,deuCerto = False):
        if deuCerto == True:
            head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.synCode, ACK_NACK = self.ackCode))
        if deuCerto == False:
            head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = self.synCode, ACK_NACK = self.nackCode))
        return(head)

    def getSize(self,file):
        head = file[0:5]
        container = self.headStruct.parse(head)
        return container["size"]

    def getSYN(self,file):
        head = file[0:5]
        container = self.headStruct.parse(head)
        return container["SYN"]

    def getACK_NACK(self,file):
        head = file[0:5]
        container = self.headStruct.parse(head)
        return container["ACK_NACK"]
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
            print("Mandei o Sync \:3")
            ack_syn = self.rx.getNData()
            if self.getACK_NACK(ack_syn) == 157 and self.getSYN(ack_syn) == 1: 
                print("Mandei o ACK \:3")
                time.sleep(1)
                self.tx.sendBuffer(self.buildACK_NACK(deuCerto=True) + self.end)
                break

            time_now = time.time()
            if (time_now - time_inicio) > 30.0:
                sys.exit()


        time.sleep(1)


        # receive syn + ack

        # receive ack

        data = (head + data + self.end)
        print(data)
        self.tx.sendBuffer(data)

    def getData(self):
        """ Get n data over the enlace interface
        Return the byte array and the size of the buffer
        """

        

        while True:
            if self.rx.getBufferLen() > 4:
                data = self.rx.getNData() # receive syn
                if self.getSYN(data) == 1:
                    print("Syn recebido, send ack + syn")
                    self.rx.clearBuffer()
                    time.sleep(0.05)
                    self.tx.sendBuffer(self.buildACK_NACK(deuCerto = True) + self.end) #ack + syn
                    time.sleep(0.1)

                    data = self.rx.getNData() #receive ack
                    if self.getACK_NACK(data) == 157:
                        print("handshake completo")
                        break


        data = self.rx.getNData()
        data, head = self.openPackage(data)
        return(data, len(data))

    def addHead(self, txLen, txBuffer):
        return (self.buildHead(txLen) + txBuffer)

    def decrypHead(self, head):
        return (struct.unpack(self.headStruct, head))

    def openPackage(self,file):

    	head = file[0:5]
    	file = file[5:-8]

    	return(file,head)

