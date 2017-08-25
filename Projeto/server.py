#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#####################################################
# Camada Física da Computação
# Prof. Rafael Corsi
#  Abril/2017
#  Aplicação
####################################################

from enlace import *
import time

# Serial Com Port
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports

serialName = "COM7"           # porta computador paulo
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
#serialName = "COM3"                  # Windows(variacao de)

def main():
    # Inicializa enlace
    com = enlace(serialName)

    # Ativa comunicacao
    com.enable()

    # Endereco da imagem a ser transmitida
    imageR = "./imgs/imageC.png"

    # Endereco da imagem a ser salva
    imageW = "./imgs/recebida.png"

    # Log
    print("-------------------------")
    print("Comunicação inicializada")
    
    print("  porta : {}".format(com.fisica.name))
    print("-------------------------")

    # Carrega imagem
    print ("Carregando imagem para transmissão :")
    print (" - {}".format(imageR))
    print("-------------------------")
    txBuffer = open(imageR, 'rb').read()
    txLen    = len(txBuffer)
    print(txLen)

    # Faz a recepção dos dados
    print ("Recebendo dados .... ")
    
    #inicio = time.time() # começa a contar o tempo

    rxBuffer, nRx = com.getData() # espera receber todos os bits -1 pois ele ja foi recebido anteriormente
    #fim = time.time() #acabou de receber
    

    # log
    print ("Lido              {} bytes ".format(nRx))

    # Salva imagem recebida em arquivo
    print("-------------------------")
    print ("Salvando dados no arquivo :")
    print (" - {}".format(imageW))
    f = open(imageW, 'wb')
    f.write(rxBuffer)
    

    # Fecha arquivo de imagem
    f.close()


    # Encerra comunicação
    print("-------------------------")
    print("Comunicação encerrada")
    print("tempo de trasmição:","?")
    print("-------------------------")
    com.disable()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.exit()
        raise e
