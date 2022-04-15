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
        self.backup = False
    def update(self):
        """Atualiza o estado do ambiente"""
        
        if self.paused == False:
            if self.status == "comeco":
                self.prepare_agentV()
                self.status = "vasculhador"

            elif self.status == "vasculhador":
                running = self.updateVasculhador()
                if not running:
                    if self.backup: self.save_agentV(self.agentV.get_maze(), self.agentV.get_victims())
                    self.prepare_agentS(self.agentV.get_maze(), self.agentV.get_victims())
                    self.status = "socorrista"
            
            elif self.status == "skip":
                maze, victims = self.load_agentV()
                self.prepare_agentS(maze, victims)
                self.status = "socorrista"

            elif self.status == "socorrista":
                running = self.updateSocorrista()
                if not running:
                    self.status = "fim"

            elif self.status == "quit":
                return False

        self.check_events()
        
        return True

    def updateVasculhador(self):
        """Atualiza o estado do ambiente para o estado do vasculhador"""
        action = self.agentV.deliberate()
        if self.agentCollision(self.agentV):
            self.agentV.comebackWall()
        if self.foundVictim(self.agentV) and not action=='V':
            self.agentV.foundVictim()

        print(f"Vasculhador posicação: {self.agentV.x}, {self.agentV.y}")
        print(f"Delibera: {action}")
        print(f"Bloco: {self.blocks[self.agentV.y][self.agentV.x].category}")
        print()
        if action: return True
        return False

    def updateSocorrista(self):
        """Atualiza o estado do ambiente para o estado do socorrista"""
        action = self.agentS.deliberate()

        print("Socorrista posição:", self.agentS.x, self.agentS.y)
        print("Delibera:", action)
        print("Vítimas socorridas:", self.agentS.get_rescued())
        print()

        if action: return True
        return False

    def prepare_agentV(self):
        """Prepara o agente vasculhador para o estado inicial"""
        self.agentV = AgentV(self.base_x, self.base_y, self.rows, self.columns, self.Bv, self.Tv)

    def prepare_agentS(self, maze=None, victims=None):
        """Prepara o agente socorrista para o estado inicial"""
        self.agentS = AgentS(self.base_x, self.base_y, self.rows, self.columns, self.Ts, self.Bs, self.Ks)
        self.agentS.set_maze(maze)
        self.agentS.set_victim(victims)
        self.agentS.makeCompleteGraph()


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

    def setTimeSleep(self, time:int):
        self.time_sleep = time

    def setBackup(self, backup:bool):
        self.backup = backup

    def generateMap(self, filename):
        """Gera um mapa de labirinto a partir de um arquivo
        @param filename: nome do arquivo
        """
        with open(filename, 'r') as f:
            lines = f.readlines()

        for line in lines: 
            line = line.split()

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
        """Desenha o labirinto na tela"""
        if self.status == "vasculhador":
            pov = 'V'
        elif self.status == "socorrista":
            pov = 'S'
        elif self.status == "fim":
            pov = 'S'
        else:
            pov = None
        self.view.draw(debug = self.debug, pov = pov)
    
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
        elif self.status == "socorrista" or self.status == "fim":
            return self.agentS
    
    def __str__(self):
        """Retorna informações do agente atual e suas coordenadas
        """
        if self.status == "comeco":
            return "Mapa construído! Preparando nosso agente vasculhador..."
        if self.status == "vasculhador":
            return f"Agente Vasculhador: ({str(self.agentV.x)}, {str(self.agentV.y)})   Tempo Restante: {str(self.agentV.time)} m    Bateria: {str(self.agentV.battery)} un"
        elif self.status == "socorrista":
            return str(self.agentS)
        else:
            text = str(self.agentS).split('|')
            text = '|'.join(text[1:])
            return "Fim (press 'q' to quit) => " + text

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
            if event == 'quit':
                self.status = 'quit'
            if event == 'debug':
                self.debug = not self.debug
                print(f"Debug: {self.debug}")

    def save_agentV(self, maze, victims):
        # salvar labirinto
        with open('maze.txt', 'w') as f:
            for line in maze:
                f.write(' '.join(list(map(str, line))) + '\n')
        # salvar vitimas
        with open('victim.txt', 'w') as f:
            for line in self.victim:
                f.write(str(line[0]) + ',' + str(line[1]) + '\n')
    def load_agentV(self):
        # carregar labirinto
        with open('maze.txt', 'r') as f:
            maze = []
            for line in f.readlines():
                maze.append(list(map(int, line.split())))
        # carregar vitimas
        with open('victim.txt', 'r') as f:
            victims = []
            for line in f.readlines():
                victims.append(tuple(map(int, line.split(','))))
        return maze, victims