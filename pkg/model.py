from view import View 
from block import Block
from agentv import AgentV
from agents import AgentS

import time
class Model:
    """Model é o modelo do ambiente. Implementa um ambiente na forma de um labirinto com paredes, agentes e vítimas.
    """
    def __init__(self, config_file, debug=False):
        
        """Construtor de modelo do ambiente físico (labirinto)
        @param rows: número de linhas do labirinto
        @param columns: número de colunas do labirinto
        """
        self.rows = config_file['maxLin']
        self.columns = config_file['maxCol']
        self.Tv = config_file['Tv']
        self.Ts = config_file['Ts']
        self.Bv = config_file['Bv']
        self.Bs = config_file['Bs']
        self.Ks = config_file['Ks']

        self.view = View(self)
        self.blocks = [[Block(x, y) for x in range(self.columns)] for y in range(self.rows)]
        self.agentV = None
        self.agentS = None
        self.victim = []

        self.status = "comeco"   
        self.paused = False
        self.time_sleep = 0.1

        self.debug = debug

    def update(self):
        """Atualiza o estado do ambiente"""

        if self.paused == False:
            if self.status == "comeco":
                self.prepare_agentV()
                self.status = "vasculhador"

            elif self.status == "vasculhador":
                running = self.updateVasculhador()
                if not running:
                    self.prepare_agentS()
                    self.status = "socorrista"
            
            elif self.status == "socorrista":
                running = self.updateSocorrista()
                if not running:
                    self.status = "fim"

            elif self.status == "fim":
                return False

        running = self.check_events()
        if running == False:
            return False
        
        return True

    def updateVasculhador(self):
        """Atualiza o estado do ambiente para o estado do vasculhador"""
        action = self.agentV.deliberate()
        if self.agentCollision(self.agentV):
            self.agentV.comebackWall()
        if self.foundVictim(self.agentV) and not action=='V':
            self.agentV.foundVictim()

        print(f"Vasculhador delibera: {self.agentV.x}, {self.agentV.y}")
        print(f"Ação: {action}")
        print(f"Bloco: {self.blocks[self.agentV.y][self.agentV.x].category}")
        print()
        if action: return True
        return False

    def updateSocorrista(self):
        """Atualiza o estado do ambiente para o estado do socorrista"""
        running = self.agentS.deliberate()

        print("Socorrista delibera:", self.agentS.x, ",", self.agentS.y)

        return running

    def prepare_agentV(self):
        """Prepara o agente vasculhador para o estado inicial"""
        self.agentV = AgentV(self.base_x, self.base_y, self.rows, self.columns, self.Bv, self.Tv)

    def prepare_agentS(self):
        """Prepara o agente socorrista para o estado inicial"""
        self.agentS = AgentS(self.base_x, self.base_y, self.rows, self.columns, self.Bs, self.Ks)

    def checkValidCoord(self, x, y):
        """Verifica se uma coordenada é válida
        @param x: coordenada x
        @param y: coordenada y
        """
        return x >= 0 and x < self.rows and y >= 0 and y < self.columns

    def setBase(self, x,y):
        self.base_x = x
        self.base_y = y
        
    def setVictim(self, x, y):
        if self.checkValidCoord(x, y):
            self.blocks[y][x].setCategory("victim")
            self.victim.append((x,y))
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
                    self.setBase(x, y)
                elif line[0] == 'Parede':
                    self.setWall(x, y)
                elif line[0] == 'Vitima':
                    self.setVictim(x, y)
                else:
                    print("Erro: linha inválida. ", line)
                    return False
        return True

    ## Desenha o labirinto na tela
    def draw(self):
        self.view.draw(debug = self.debug)
    
    def foundVictim(self, agent):
        """Verifica se o agente encontrou a vítima
        """
        return self.blocks[agent.y][agent.x].category == "victim"
    def agentCollision(self, agent):
        """Verifica se houve colisão entre agente e parede
        """
        if agent.x < 0 or agent.x >= self.rows or agent.y < 0 or agent.y >= self.columns:
            return True
        elif self.blocks[agent.y][agent.x].category == "wall":
            return True
        else:
            return False

    def getAgent(self):
        if self.status == "vasculhador":
            return self.agentV
        elif self.status == "socorrista":
            return self.agentS
    
    def __str__(self):
        """Retorna informações do agente atual e suas coordenadas
        """
        if self.status == "comeco":
            return "Mapa construído! Preparando nosso agente vasculhador..."
        if self.status == "vasculhador":
            return f"Agente Vasculhador: ({str(self.agentV.x)}, {str(self.agentV.y)})   Tempo Restante: {str(self.agentV.time)} m    Bateria: {str(self.agentV.battery)} un"
        elif self.status == "socorrista":
            return f"Agente Socorrista: ({str(self.agentS.x)}, {str(self.agentS.y)})... A DEFINIR"
        else:
            return "Fim"

    def setTimeSleep(self, time):
        self.time_sleep = time
    def getTimeSleep(self):
        return self.time_sleep

    def check_events(self):
        event = None
        for event in self.view.keyboard_event():
            if event == 'pause':
                if self.paused:
                    self.paused = False
                    print("Resume")
                else:
                    self.paused = True
                    print("Pause")
            if event == '-':
                self.time_sleep *= 1.1
                print(f"Time Sleep: {self.time_sleep}")
            if event == '+':
                self.time_sleep *= 0.91
                print(f"Time Sleep: {self.time_sleep}")
            if event == 'exit':
                return False
            if event == 'debug':
                self.debug = not self.debug
                print(f"Debug: {self.debug}")
        return True