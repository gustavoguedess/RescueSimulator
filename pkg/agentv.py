from block import Block

class AgentV(Block):
    """
    AgentV: Agente Vasculhador 
    """

    def __init__(self, x, y, rows, columns):
        super().__init__(x, y, "agent")
        self.x_base = x
        self.y_base = y
        self.rows = rows
        self.columns = columns
        self.visited = [[False for x in range(columns)] for y in range(rows)]
        self.stack = []
        self.plan = []
        self.last_position = (-1,-1)
        self.visitme()

    def move(self, direction):
        if direction == "N":
            self.y -= 1
        elif direction == "S":
            self.y += 1
        elif direction == "E":
            self.x += 1
        elif direction == "W":
            self.x -= 1
        elif direction == "NE":
            self.x += 1
            self.y -= 1
        elif direction == "SE":
            self.x += 1
            self.y += 1
        elif direction == "NW":
            self.x -= 1
            self.y -= 1
        elif direction == "SW":
            self.x -= 1
            self.y += 1

    def deliberate(self):
        #Caso não tenha um plano, cria um plano.  
        if not self.plan:
            # Retorna a coordenada não visitada mais próxima
            x, y = self.dfs()

            # Se tiver coordenada não visitada, cria um plano para chegar nela
            if x is not None and y is not None:
                self.plan = self.makePlan(x, y)
            # Senão o plano é voltar para a base
            else:
                self.plan = self.makePlan(self.x_base, self.y_base)
            
        # Salva a posição atual
        self.last_position = (self.x, self.y)

        # Move para a próxima coordenada do plano
        self.x, self.y = self.plan.pop(0)
        print('Agente Vasculhador delibera:', self.x, self.y)

        # Marca a coordenada como visitada
        self.visitme()
        
        return True

    def directionCoord(self, direction):
        if direction == "N":   return self.x, self.y-1
        elif direction == "S": return self.x, self.y+1
        elif direction == "E": return self.x+1, self.y
        elif direction == "W": return self.x-1, self.y
        elif direction == "NE":return self.x+1, self.y-1
        elif direction == "SE":return self.x+1, self.y+1
        elif direction == "NW":return self.x-1, self.y-1
        elif direction == "SW":return self.x-1, self.y+1
    
    def dfs(self):
        """
        DFS: Busca em profundidade
            Retorna a próxima coordenada não visitada
        """
        for direction in ["NW", "NE", "SW", "SE", "N", "W", "E", "S"]:
            x, y = self.directionCoord(direction)
            if self.checkValidCoord(x, y) and not self.visited[y][x]:
                self.stack.append((x, y))

        # Próxima coordenada não visitada da pilha
        while self.stack:
            x, y = self.stack.pop(-1)
            if not self.visited[y][x]:
                return x, y
        return None, None

    def comeback(self):
        """
        Volta ao estado anterior ou retorna False caso não haja estado anterior
        """
        if self.last_position == (-1,-1):
            return False
        self.x, self.y = self.last_position
        self.last_position = (-1,-1)
        return True

    def makePlan(self, x, y):
        """
        Cria um plano de coordenadas
        @param x: coordenada x
        @param y: coordenada y
        """
        plan = []
        
        #TODO - Implementar o algoritmo de criação de plano
        #TODO Provavelmente é o algoritmo de busca em largura

        # O plano atual é simplesmente um teleporte para a coordenada x, y (ERRADO)
        plan.append((x, y))

        return plan
    
    def makePlanBase(self):
        """
        Cria um plano para o agente chegar na Base
        """
        self.plan = self.makePlan(self.x_base, self.y_base)

    def visitme(self):
        self.visited[self.y][self.x] = True

    def checkValidCoord(self, x, y):
        """Verifica se uma coordenada é válida
        @param x: coordenada x
        @param y: coordenada y
        """
        return x >= 0 and x < self.rows and y >= 0 and y < self.columns

    def __str__(self):
        return f"Agente ({self.x}, {self.y})"