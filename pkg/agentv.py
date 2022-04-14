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

        self.time = 0
        self.Bv = Bv
        self.Tv = Tv

        self.battery = Bv
        self.time = Tv

        self.directions = ["N", "S", "E", "W" , "NE", "SE", "NW", "SW"]
        self.action_cost = {
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
            B: Bloqueado|Parede
        """
        self.plan = []
        
        self.cost_to_base = [[-1 for x in range(columns)] for y in range(rows)]
        self.direction_to_base = [['P' for x in range(columns)] for y in range(rows)]
        
        self.cost_to_agent = [[-1 for x in range(columns)] for y in range(rows)]
        self.direction_to_agent = [["P" for x in range(columns)] for y in range(rows)]

        self.last_position = (-1,-1)
        self.visited = [[False for x in range(columns)] for y in range(rows)]
        self.visitme()

        self.victims = []
        self.found_victim = False

    def deliberate(self):
        """
            Deliberate: Decide como o agente deve se movimentar
        """
        ## Recarregar
        if self.atBase() and self.battery < self.Bv and self.checkCostTo(self.x, self.y, action='R')<=self.time:
            self.plan = ['R']

        ## Analisa a vítima
        elif self.found_victim and self.checkCostTo(self.x, self.y, action='V')<=self.battery:
            self.plan = ['V']
            self.victims.append((self.x, self.y))
            self.found_victim = False
        
        ## Cria um plano de movimento
        elif not self.plan:
            x, y = self.nearest_block(self.x, self.y)

            
            if not self.validCoord(x, y):
                x,y = self.base_x, self.base_y
            cost_to_goal = self.checkCostTo(x, y)
            if cost_to_goal>self.battery or cost_to_goal>self.time:
                x,y = self.base_x, self.base_y
            
            self.plan = self.makePlan(x, y)
            

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
            self.battery-= self.action_cost[action]
    
    def updateTime(self, action):
        """ Diminui o tempo do agente """
        self.time-= self.action_cost[action]

    def checkCostTo(self, x, y, action=None):
        """ Verifica o custo em tempo de movimento para a coordenada x, y """
        if action=='A':
            return self.action_cost[action] + self.cost_to_base[y][x]
        elif action=='R':
            return self.action_cost[action]
        return self.cost_to_agent[y][x] + self.cost_to_base[y][x]

    def lee(self, x, y, walls=None):
        """Lee: Busca em largura para encontrar o caminho mais curto a partir de uma coordenada considerando paredes"""
        directionmap = [['P' for x in range(self.columns)] for y in range(self.rows)]
        costmap = [[-1 for x in range(self.columns)] for y in range(self.rows)]
    
        nearests = []
        nearest_cost = None
        costmap[y][x] = 0
        queue = [{'x':x,'y':y, 'cost':0}]
        
        while queue:
            item = queue.pop(0)
            x = item['x']
            y = item['y']
            cost = item['cost']

            if self.visited[y][x]==False:
                if nearest_cost is None or cost<=nearest_cost:
                   nearests.append((x,y))
                   nearest_cost = cost
            else:
                for direction in self.directions:
                    x_new, y_new = self.directionCoord(direction, x, y)
                    #Se for válido, não foi visitado e não é uma parede
                    if self.validCoord(x_new, y_new) and walls[y_new][x_new]=='B':
                        directionmap[y_new][x_new] = 'B'
                    elif self.validMove(x, y, direction) and costmap[y_new][x_new]==-1:
                        costmap[y_new][x_new] = cost + self.action_cost[direction]
                        directionmap[y_new][x_new] = self.oppositeDirection(direction)
                        self.insert_sorted_list(queue, {'x':x_new,'y':y_new, 'cost':costmap[y_new][x_new]})
                        #self.printDirections(directionmap)
            
        #get min cost from nearests
        nearest = None
        for x,y in nearests:
            if nearest is None: 
                nearest = (x,y)
            elif self.cost_to_base[y][x]<self.cost_to_base[nearest[1]][nearest[0]]:
                nearest = (x,y)

        return costmap, directionmap, nearest

    def validMove(self, x, y, direction):
        """ Verifica se a coordenada x, y pode ser movida para a direção direction """
        x_new, y_new = self.directionCoord(direction, x, y)
        if self.validCoord(x_new, y_new) == False:
            return False
        if self.direction_to_base[y_new][x_new]=='B':
            return False
        if len(direction)==1:
            return True
        d1, d2 = list(direction)
        x1, y1 = self.directionCoord(d1, x, y)
        x2, y2 = self.directionCoord(d2, x, y)
        if self.direction_to_base[y1][x1]=='B' and self.direction_to_base[y2][x2]=='B':
            return False
        return True

    def move(self, direction):
        self.x, self.y = self.directionCoord(direction, self.x, self.y)

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

    def oppositeDirection(self, direction):
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
            if lst[m]['cost'] < item['cost']:
                i = m + 1
            else:
                f = m
        lst.insert(i, item)
        return lst

    def nearest_block(self, x, y):
        """
        nearest_block: Busca pelo bloco mais próximo do agente de menor tamanho que ainda não foi visitado
            Retorna a próxima coordenada desse bloco
        """

        #Calcula a distância de cada bloco para a base
        self.cost_to_base, self.direction_to_base, _ = self.lee(self.base_x, self.base_y, self.direction_to_base)

        #Calcula a distância de cada bloco para o agente
        self.cost_to_agent, self.direction_to_agent, block = self.lee(self.x, self.y, self.direction_to_base)
        
        if block is None: return None, None
        return block
        
    def comebackWall(self):
        """
        Volta ao estado anterior ou retorna False caso não haja estado anterior
        """
        self.direction_to_base[self.y][self.x] = "B"
        self.direction_to_agent[self.y][self.x] = "B"
        self.cost_to_base[self.y][self.x] = -1

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
        while x != self.x or y != self.y:
            direction = self.direction_to_agent[y][x]
            plan.insert(0,self.oppositeDirection(direction))
            x, y = self.directionCoord(self.direction_to_agent[y][x], x, y)
            
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


    ####################################################################################################################
    def printDirections(self, directions):
        """
        Imprime as direções de cada bloco
        """
        for y in range(self.rows):
            for x in range(self.columns):
                print(directions[y][x].ljust(2, ' '), end=" ")
            print()

    def printBaseDirections(self):
        """
        Imprime as direções de cada bloco
        """
        self.printDirections(self.direction_to_base)
            
    def printCostToBase(self):
        """
        Imprime o custo para chegar a base de cada bloco
        """
        for y in range(self.rows):
            for x in range(self.columns):
                print(str(self.cost_to_base[y][x]).ljust(4, ' '), end=" ")
            print()

    def printAgentDirections(self):
        """
        Imprime as direções de cada bloco
        """
        self.printDirections(self.direction_to_agent)

    def cost_block(self, block, by="agent"):
        if by == "agent":
            return self.cost_to_agent[block.y][block.x]
        else:
            return self.cost_to_base[block.y][block.x]
    
    def get_maze(self):
        maze = [[0 for x in range(self.columns)] for y in range(self.rows)]
        for y in range(self.rows):
            for x in range(self.columns):
                if self.visited[y][x] and self.direction_to_base[y][x] != "B":
                    maze[y][x] = 1
        return maze

    def get_victims(self):
        return self.victims