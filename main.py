import sys
import os
import time

## Importa as classes que serao usadas
sys.path.append(os.path.join("pkg"))
from model import Model

## Metodo utilizado para permitir que o usuario construa o labirindo clicando em cima
def buildMaze(model):
    model.drawToBuild()
    step = model.getStep()
    while step == "build":
        model.drawToBuild()
        step = model.getStep()
    ## Atualiza o labirinto
    model.updateMaze()

def getConfig():
    arq = open(os.path.join("config_data","config.txt"),"r")
    configDict = {} 
    for line in arq:
        ## O formato de cada linha é:var=valor
        ## As variáveis são 
        ##  maxLin, maxCol que definem o tamanho do labirinto
        ## Tv e Ts: tempo limite para vasculhar e tempo para salvar
        ## Bv e Bs: bateria inicial disponível ao agente vasculhador e ao socorrista
        ## Ks :capacidade de carregar suprimentos em número de pacotes (somente para o ag. socorrista)

        values = line.split("=")
        configDict[values[0]] = int(values[1])

    return configDict

def main():
    ## Inicializa o labirinto
    configDict = getConfig()
    print("dicionario config: ", configDict)
    model = Model(configDict["maxLin"], configDict["maxCol"])

    ## Construa o labirinto
    filename=os.path.join("config_data","ambiente.txt")
    model.generateMap(filename)

    model.draw()
    time.sleep(5)


if __name__ == '__main__':
    main()
