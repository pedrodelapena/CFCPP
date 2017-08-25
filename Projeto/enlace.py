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
    headSTART = "S.C.H.S.".encode() #super clever head start
    headStruct = Struct("start" / Int8ub,"size" / Int16ub,"SYN" / Int8ub,"ACK" / Int8ub )
    ackCode = "deu certo!".encode()
    nackCode = "a casa caiu".encode()

    m = hashlib.sha256()
    m.update("Nobody inspects the spammish repetition".encode("UTF-8"))

    synCode = m.hexdigest()


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
        head = self.headStruct.build(dict(start = self.headSTART,size = dataLen))
        return(head)

    def buildSync(self, dataLen):
        head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = synCode))
        return(head)

    def buildACK(self, dataLen,deuCerto):
        if deuCerto == True:
            head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = synCode, ACK = ackCode))
        if deuCerto == False:
            head = self.headStruct.build(dict(start = self.headSTART,size = dataLen, SYN = synCode, ACK = nackCode))
        return(head)

    ################################
    # Application  interface       #
    ################################
    def sendData(self, txLen, txBuffer):
        """ Send data over the enlace interface
        """
        data = self.addHead(txLen, txBuffer) + self.end
        self.tx.sendBuffer(data)

    def getData(self):
        """ Get n data over the enlace interface
        Return the byte array and the size of the buffer
        """
        data = self.rx.getNData()
        data = self.rx.openPackege(data)
        return(data, len(data))
        
    def addHead(self, txLen, txBuffer):
        return (self.buildHead(txLen) + txBuffer)

