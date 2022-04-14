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

def getConfig(filename):
    arq = open(os.path.join(filename),"r")
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

def get_args():
    """
    Parse the command line arguments
    """
    import argparse
    parser = argparse.ArgumentParser(description="Maze Rescue")
    parser.add_argument("-i -c", "--input_config", help="Input config", default="config_data/config.txt")
    parser.add_argument("-a", "--ambiente", help="Input 'ambiente' config", default="config_data/ambiente.txt")
    parser.add_argument("-d", "--debug", help="Debug mode", action="store_true")
    parser.add_argument("-s", "--skip", help="Skip mode", action="store_true", default=False)
    args = parser.parse_args()
    return args

def main():

    args = get_args()
    print(args.debug)

    ## Inicializa o labirinto
    configDict = getConfig(args.input_config)
    print("dicionario config: ", configDict)
    model = Model(configDict, debug=args.debug)

    ## Construa o labirinto
    filename=os.path.join(args.ambiente)
    model.generateMap(filename)
    model.draw()
    #time.sleep(3)

    if args.skip:
        print(args.skip)
        model.status = "skip"
        print("Skip")
        time.sleep(2)

    running = True
    while running:
        running = model.update()
        model.draw()
        time.sleep(model.time_sleep)
    
    model.draw()
if __name__ == '__main__':
    main()