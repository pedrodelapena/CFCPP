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
    headSTART = 0xFF #super clever head start
    headStruct = Struct("start" / Int8ub,"size" / Int16ub,"SYN" / Int8ub,"ACK_NACK" / Int8ub )
    ackCode = 0x9d
    nackCode = 0x0e
    synCode = 0x01

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
        head = headStruct.build(dict(start = headSTART,size = dataLen, SYN = fakeSyn, ACK_NACK = fakeAck))
        return(head)

    def buildSync(self, dataLen):
        head = headStruct.build(dict(start = headSTART,size = dataLen, SYN = synCode, ACK_NACK = fakeAck))
        return(head)

    def buildACK_NACK(self, dataLen,deuCerto):
        if deuCerto == True:
            head = headStruct.build(dict(start = headSTART,size = dataLen, SYN = synCode, ACK_NACK = ackCode))
        if deuCerto == False:
            head = headStruct.build(dict(start = headSTART,size = dataLen, SYN = synCode, ACK_NACK = nackCode))
        return(head)

    def getSize(self,head):
        container = headStruct.parse(head)
        return container["size"]

    def getSYN(self,head):
        container = headStruct.parse(head)
        return container["SYN"]

    def getACK_NACK(self,head):
        container = headStruct.parse(head)
        return container["ACK_NACK"]
    ################################
    # Application  interface       #
    ################################
    def sendData(self, txLen, txBuffer):
        """ Send data over the enlace interface
        """
        data += self.end
        self.tx.sendBuffer(data)

    def getData(self):
        """ Get n data over the enlace interface
        Return the byte array and the size of the buffer
        """
        data = self.rx.getNData()
        data, head = self.openPackege(data)
        return(data, len(data))
        
    def addHead(self, txLen, txBuffer):
        return (self.buildHead(txLen) + txBuffer)

    def decrypHead(self, head):
        return (struct.unpack(self.headStruct, head))

    def openPackage(self,file):

    	head = file[0:5]
    	file = file[5:-8]

    	return(file,head)

