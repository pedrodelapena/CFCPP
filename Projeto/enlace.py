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

# Interface Física
from interfaceFisica import fisica

# enlace Tx e Rx
from enlaceRx import RX
from enlaceTx import TX



class enlace(object):
    """ This class implements methods to the interface between Enlace and Application
    """
    headSTART = 0XFF #super clever head start
    headStruct = Struct("start" / Int8ub,"size" / Int16ub )

    def __init__(self, name):
        """ Initializes the enlace class
        """
        self.fisica      = fisica(name)
        self.rx          = RX(self.fisica)
        self.tx          = TX(self.fisica)
        self.connected   = False

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

    ################################
    # Application  interface       #
    ################################
    def sendData(self, txLen, txBuffer):
        """ Send data over the enlace interface
        """
        size = txLen//255
        modulo = txLen%255

        data = "S.C.H.E.".encode() + size + modulo + txBuffer + "s.t.o.p.".encode()
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

