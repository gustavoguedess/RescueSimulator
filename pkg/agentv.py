from block import Block

class AgentV(Block):
    """
    AgentV: Agente Vasculhador 
    """

    def __init__(self, x, y, rows, columns, Bv, Tv):
        super().__init__(x, y, "agentv")
        self.base_x = x
        self.base_y = y

        self.rows = rows
        self.columns = columns

        self.last_position = (-1,-1)
        self.visited = [[False for x in range(columns)] for y in range(rows)]
        self.visitme()

        self.found_victim = False

        self.time = 0
        self.Bv = Bv
        self.Tv = Tv

        self.battery = Bv
        self.time = Tv

        self.directions = ["N", "S", "E", "W" , "NE", "SE", "NW", "SW"]
        self.costs = {
            "N": 1, "S": 1, "E": 1, "W": 1,
            "NE": 1.5, "SE": 1.5, "NW": 1.5, "SW": 1.5,
            "R": 240, "V": 2
        }
        """ Legenda
            N: Norte
            S: Sul
            E: Leste
            W: Oeste
            NE: Norte Leste
            SE: Sul Leste
            NW: Norte Oeste
            SW: Sul Oeste
            R: Recarregar
            V: Vítima 
            P: Parado
        """
        self.wave_expansion()
        self.plan = []
        
        self.dest_direction = [["P" for x in range(columns)] for y in range(rows)]

    def deliberate(self):
        """
            Deliberate: Decide como o agente deve se movimentar
        """
        if self.atBase() and self.battery < self.Bv:
            print(F"Agente x: {self.x} y: {self.y}, Base x: {self.base_x} y: {self.base_y}, battery: {self.battery}")
            self.plan = ['R']
        elif self.found_victim and self.checkCostTo(self.x, self.y, action='V')<=self.battery:
            self.plan = ['V']
            self.found_victim = False
        elif not self.plan:
            x, y = self.nearest_block_lee(self.x, self.y)
            # if self.validCoord(x, y):
            #     print(f"Custo: {self.checkCostTo(self.x, self.y)} | Bateria: {self.battery} | Tempo: {self.time}")
            if not self.validCoord(x, y) or self.checkCostTo(x, y)>self.battery:
                x,y = self.base_x, self.base_y
            
            print(f"Agente x: {self.x} y: {self.y}, Base x: {self.base_x} y: {self.base_y}, battery: {self.battery}")
            self.plan = self.makePlan(x, y)
            print(self.plan)
            
            print(f"Plano do agente: {self.plan}")
            if len(self.plan)>1:
                import time
                time.sleep(10)

        if not self.plan:
            return False

        self.last_position = (self.x, self.y)
        action = self.plan.pop(0)
        if action in self.directions:
            self.move(action)
            self.visitme()   

        self.updateBattery(action)
        self.updateTime(action)
        return action

    def foundVictim(self):
        """ Achou uma vítima """
        self.found_victim = True
        
    def updateBattery(self, action):
        """ Atualiza a bateria do agente """
        if action in ["R"]:
            self.battery = self.Bv
        else:
            self.battery-= self.costs[action]
    
    def updateTime(self, action):
        """ Diminui o tempo do agente """
        self.time-= self.costs[action]

    def checkCostTo(self, x, y, action=None):
        """ Verifica o custo em tempo de movimento para a coordenada x, y """
        if action=='A':
            return self.costs[action] + self.base_dist[y][x]
        return self.dist_agent[y][x] + self.base_dist[y][x]

    def wave_expansion(self):
        """
        wave_expansion: Cria uma matriz de tamanho rows e largura columns com os valores de distância
        """
        self.base_dist = [[-1 for x in range(self.columns)] for y in range(self.rows)]
        self.base_direction = [['P' for x in range(self.columns)] for y in range(self.rows)]
        self.base_dist[self.base_y][self.base_x] = 0
        queue = [{'x': self.base_x, 'y': self.base_y, 'dist': 0}]
        while queue:
            item = queue.pop(0)
            x = item['x']
            y = item['y']
            for direction in self.directions:
                x_next, y_next = self.directionCoord(direction, x, y)
                if self.validCoord(x_next, y_next):
                    if self.base_dist[y_next][x_next] == -1:
                        self.base_dist[y_next][x_next] = self.base_dist[y][x] + self.costs[direction]
                        self.base_direction[y_next][x_next] = self.invertDirection(direction)
                        self.insert_sorted_list(queue, {'x': x_next, 'y': y_next, 'dist': self.base_dist[y_next][x_next]})
        for i in range(self.rows):
            print(self.base_dist[i])
        return self.base_dist

    def move(self, direction):
        self.x, self.y = self.directionCoord(direction, self.x, self.y)

        self.base_dist[self.y][self.x] = -1
        for direction in self.directions:
            x,y = self.directionCoord(direction, self.x, self.y)
            if self.visited[y][x]:
                if self.base_dist[self.y][self.x] > self.base_dist[y][x]+self.costs[direction] or self.base_dist[self.y][self.x] == -1:
                    self.base_dist[self.y][self.x] = self.base_dist[y][x] + self.costs[direction]
                    self.base_direction[self.y][self.x] = self.invertDirection(direction)

    def directionCoord(self, direction:str, x=-1, y=-1):
        if x == -1: 
            x = self.x
            y = self.y
        if direction == "N":   return x, y-1
        elif direction == "S": return x, y+1
        elif direction == "E": return x+1, y
        elif direction == "W": return x-1, y
        elif direction == "NE":return x+1, y-1
        elif direction == "SE":return x+1, y+1
        elif direction == "NW":return x-1, y-1
        elif direction == "SW":return x-1, y+1
    
    def coordDirection(self, x1, y1, x2, y2):
        """
        Retorna a direção para a coordenada x2, y2 a partir da coordenada x1, y1
        """
        #Se não tiver um bloco de distância
        if abs(x1 - x2) > 1 or abs(y1 - y2) > 1:
            return "P"
        if x1 == x2:
            if y1 < y2:
                return "S"
            else:
                return "N"
        elif y1 == y2:
            if x1 < x2:
                return "E"
            else:
                return "W"
        elif x1 < x2 and y1 < y2:
            return "SE"
        elif x1 < x2 and y1 > y2:
            return "NE"
        elif x1 > x2 and y1 < y2:
            return "SW"
        elif x1 > x2 and y1 > y2:
            return "NW"
    def invertDirection(self, direction):
        if direction == "N": return "S"
        elif direction == "S": return "N"
        elif direction == "E": return "W"
        elif direction == "W": return "E"
        elif direction == "NE": return "SW"
        elif direction == "SE": return "NW"
        elif direction == "NW": return "SE"
        elif direction == "SW": return "NE"

    def insert_sorted_list(self, lst, item):
        """Insere um item na lista ordenada"""
        i = 0
        f = len(lst)
        while i < f:
            m = (i + f) // 2
            if lst[m]['dist'] < item['dist']:
                i = m + 1
            else:
                f = m
        lst.insert(i, item)
        return lst

    def nearest_block_lee(self, x, y):
        """
        nearest_block_lee: Busca pelo bloco mais próximo do agente de menor tamanho que ainda não foi visitado utilizando o algoritmo de Lee
            Retorna a próxima coordenada desse bloco
        """
        
        def check_nearest_from_base(block, check_block):
            """Checa se o bloco é o mais próximo de base"""
            if not self.validCoord(check_block.x, check_block.y):  
                return block
            if self.visited[check_block.y][check_block.x]:              
                return block
            if block is None:    

                return check_block
            
            if self.base_dist[block.y][block.x] > self.base_dist[check_block.y][check_block.x]:                           
                return check_block
            return block
            
        

        block = None
        max_dist = max(self.rows, self.columns)
        self.dist_agent = [[-1 for x in range(self.columns)] for y in range(self.rows)]

        item = {'x': x, 'y': y, 'dist': 0}
        self.dest_direction[y][x] = "C"
        self.dist_agent[y][x] = 0
        stack = [item]

        while stack:
            item = stack.pop(0)
            x = item['x']
            y = item['y']
            dist = self.dist_agent[y][x]

            if dist > max_dist:
                break
            if not self.visited[y][x]:
                print(f"x: {x}, y: {y} dist: {dist} dist_base: {self.base_dist[y][x]}")
                max_dist = dist
                block = check_nearest_from_base(block, Block(x, y))

            for direction in self.directions:
                x_next, y_next = self.directionCoord(direction, x, y)
                if self.validCoord(x_next, y_next):
                    if self.dist_agent[y_next][x_next]==-1 and self.dest_direction[y_next][x_next] is not "P":

                        self.dest_direction[y_next][x_next] = self.invertDirection(direction)
                        self.dist_agent[y_next][x_next] = dist + self.costs[direction]
                        self.insert_sorted_list(stack, {'x': x_next, 'y': y_next, 'dist': self.dist_agent[y_next][x_next]})
                        
        if block is None:
            return None, None

        return block.x, block.y
        
    def comebackWall(self):
        """
        Volta ao estado anterior ou retorna False caso não haja estado anterior
        """
        self.dest_direction[self.y][self.x] = "WALL"
        self.base_dist[self.y][self.x] = 2**10
        if self.last_position == (-1,-1):
            return False
        self.x, self.y = self.last_position
        self.last_position = (-1,-1)
        return True

    def printDirections(self):
        """
        Imprime as direções de cada bloco
        """
        for y in range(self.rows):
            for x in range(self.columns):
                print(self.dest_direction[y][x], end=" ")
            print()

    def makePlan(self, x, y):
        """
        Cria um plano de coordenadas
        @param x: coordenada x
        @param y: coordenada y
        """
        plan = []
        while self.dest_direction[y][x] != "C":
            direction = self.dest_direction[y][x]
            print(f"Direction: {direction}")
            plan.insert(0,self.invertDirection(direction))
            x, y = self.directionCoord(self.dest_direction[y][x], x, y)
            
        return plan
    
    def makePlanBase(self):
        """
        Cria um plano para o agente chegar na Base
        """
        self.plan = self.makePlan(self.base_x, self.base_y)

    def visitme(self):
        self.visited[self.y][self.x] = True

    def validCoord(self, x, y):
        """Verifica se uma coordenada é válida
        @param x: coordenada x
        @param y: coordenada y
        """
        if not isinstance(x, int) or not isinstance(y, int):
            return False
        return x >= 0 and x < self.rows and y >= 0 and y < self.columns

    def atBase(self):
        return self.x == self.base_x and self.y == self.base_y

    def __str__(self):
        return f"Agente ({self.x}, {self.y})"