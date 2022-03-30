from view import View 
from block import Block
from agentv import AgentV
from agents import AgentS

import time
class Model:
    """Model é o modelo do ambiente. Implementa um ambiente na forma de um labirinto com paredes, agentes e vítimas.
    """
    def __init__(self, config_file):
        
        """Construtor de modelo do ambiente físico (labirinto)
        @param rows: número de linhas do labirinto
        @param columns: número de colunas do labirinto
        """
        self.rows = config_file['maxLin']
        self.columns = config_file['maxCol']
        self.Tl = config_file['Tl']
        self.Ts = config_file['Ts']
        self.Bv = config_file['Bv']
        self.Bs = config_file['Bs']
        self.Ks = config_file['Ks']

        self.view = View(self)
        self.blocks = [[Block(x, y) for x in range(self.columns)] for y in range(self.rows)]
        self.agentV = None
        self.victim = []

        self.status = "vasculhador"        
    def checkValidCoord(self, x, y):
        """Verifica se uma coordenada é válida
        @param x: coordenada x
        @param y: coordenada y
        """
        return x >= 0 and x < self.rows and y >= 0 and y < self.columns

    def setAgent(self, x,y):
        self.agentV = AgentV(x, y, self.rows, self.columns)
        self.agentS = AgentS(x, y, self.rows, self.columns)
    def setVictim(self, x, y):
        if self.checkValidCoord(x, y):
            self.blocks[y][x].setCategory("victim")
        else:
            print("Erro: coordenada inválida")

    def setWall(self, x, y):
        if self.checkValidCoord(x, y):
            self.blocks[y][x].setCategory("wall")
        else:
            print("Erro: coordenada inválida")

    def generateMap(self, filename):
        """Gera um mapa de labirinto a partir de um arquivo
        @param filename: nome do arquivo
        """
        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines: 
            line = line.split()
            print(line)

            for coord in line[1:]:
                coord = coord.split(',')
                x = int(coord[0])
                y = int(coord[1])

                if line[0] == 'Agente':
                    self.setAgent(x, y)
                elif line[0] == 'Parede':
                    self.setWall(x, y)
                elif line[0] == 'Vitima':
                    self.setVictim(x, y)
                else:
                    print("Erro: linha inválida. ", line)
                    return False
        return True

    def updateVasculhador(self):
        """Atualiza o estado do ambiente para o estado do vasculhador
        """
        print("Vasculhador está atualizando")
        running = self.agentV.deliberate()
        if not running:
            self.status = "socorrista"
            return False 

        print("Agente Vasculhador está no bloco:", self.blocks[self.agentV.y][self.agentV.x].category)
        if self.agentCollision(self.agentV):
            self.agentV.comeback()

    def updateSocorrista(self):
        """Atualiza o estado do ambiente para o estado do socorrista
        """
        print("Socorrista está atualizando")
        running = self.agentS.deliberate()
        if not running:
            self.status = "fim"
            return
    def update(self):
        """Atualiza o estado do ambiente
        """

        if self.status == "vasculhador":
            self.updateVasculhador()
        elif self.status == "socorrista":
            self.updateSocorrista()
        elif self.status == "fim":
            return False
        return True

    ## Desenha o labirinto na tela
    def draw(self):
        self.view.draw()
    
    def agentCollision(self, agent):
        """Verifica se houve colisão entre agente e parede
        """
        if agent.x < 0 or agent.x >= self.rows or agent.y < 0 or agent.y >= self.columns:
            return True
        elif self.blocks[agent.y][agent.x].category == "wall":
            return True
        else:
            return False

    def printWallCoords(self):
        """Imprime as coordenadas das paredes
        """
        for i in range(self.rows):
            for j in range(self.columns):
                if self.blocks[i][j].category == "wall":
                    print("(", i, ",", j, ")")
    
    def getAgent(self):
        if self.status == "vasculhador":
            return self.agentV
        elif self.status == "socorrista":
            return self.agentS