from block import Block

class AgentS(Block):
    """
    AgentV: Agente Vasculhador 
    """

    def __init__(self, x, y, rows, columns, Ts, Bs, Ks):
        super().__init__(x, y, "agents")
        self.base_x = x
        self.base_y = y
        self.rows = rows
        self.columns = columns
        
        self.Bs = Bs
        self.Ts = Ts
        self.Ks = Ks
        self.battery = Bs
        self.time = Ts
        self.packages = Ks

        self.rescued = 0

        self.directions = ["N", "S", "E", "W" , "NE", "SE", "NW", "SW"]
        self.action_cost = {
            "N": 1, "S": 1, "E": 1, "W": 1,
            "NE": 1.5, "SE": 1.5, "NW": 1.5, "SW": 1.5,
            "R": 240, "P": 0.5, "V": 0.5
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
        """

        self.plans = {}
        self.visited = {}
        self.nearests = {}
        self.cost = {}
        
        self.plan = []

    def deliberate(self):
        """Decide o que fazer"""
        origin = (self.x, self.y)
        base = (self.base_x, self.base_y)
        # Se estiver na base, recarrega
        if origin == base and self.battery < self.Bs and self.get_cost(origin, action='R') < self.time:
            self.plan = ['R']
        elif origin in self.victims:
            self.plan = ['V']
        # Se não tiver pacotes, vai para a base
        elif not self.plan and self.packages <= 0:
            base = (self.base_x, self.base_y)
            self.plan = self.plans[origin][base]
        
        # Se estiver sem plano, procura um plano de menor custo
        elif not self.plan:
            dest = base        
            while dest==base or self.visited[dest]:
                if len(self.nearests[origin])<=0:
                    dest = (self.base_x, self.base_y)
                    break
                dest = self.nearests[origin].pop(0)
            print(f"Escolhendo Destino: {dest} / {self.cost[origin, dest]}")
            
            self.visited[dest] = True
            plan_cost = self.get_cost(origin, dest)
            if plan_cost>self.time or plan_cost>self.battery:
                dest = base
            self.plan = self.plans[origin][dest]
            
        if not self.plan:
            return False
        
        print(f"Plan: {self.plan}")

        action = self.plan.pop(0)
        if action in self.directions:
            self.move(action)
        if action == "V":
            self.found_victim()

        self.updateCost(action)

        return action
    
    def get_cost(self, origin, dest=None, action=None):
        """Retorna o custo de uma trajetória
        @param origin: coordenada de origem
        @param dest: coordenada de destino
        """
        base = (self.base_x, self.base_y)
        if action == 'R':
            cost = self.action_cost[action]
        else:
            cost = self.action_cost["P"] + self.cost[origin,dest] + self.cost[dest,base]
        return cost

    def move(self, direction):
        self.x, self.y = self.directionCoord(direction, self.x, self.y)
        self.battery-= self.action_cost[direction]
        self.time-= self.action_cost[direction]

    def found_victim(self):
        self.rescued += 1
        self.victims.remove((self.x, self.y))

    def updateCost(self, action):
        """ Atualiza o custo do agente """
        self.updateBattery(action)
        self.updateTime(action)
        self.updatePackage(action)

    def updateBattery(self, action):
        """ Atualiza a bateria do agente """
        if action in ["R"]:
            self.battery = self.Bs
        else:
            self.battery-= self.action_cost[action]
    
    def updateTime(self, action):
        """ Diminui o tempo do agente """
        self.time-= self.action_cost[action]
    
    def updatePackage(self, action):
        """ Atualiza o número de pacotes """
        if action == "R":
            diff = min(self.Ks - self.packages, self.time*2)
            self.time -= diff * self.action_cost["P"]
            self.packages+= diff
        elif action == "V":
            self.packages -= 1

    def checkValidCoord(self, x, y):
        """Verifica se uma coordenada é válida
        @param x: coordenada x
        @param y: coordenada y
        """
        return x >= 0 and x < self.rows and y >= 0 and y < self.columns

    def set_maze(self, maze):
        self.maze = maze
    
    def set_victim(self, victims):
        self.victims = victims
    
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
    
    def validCoord(self, x, y):
        """Verifica se uma coordenada é válida
        @param x: coordenada x
        @param y: coordenada y
        """
        if not isinstance(x, int) or not isinstance(y, int):
            return False
        if x < 0 or x >= self.rows or y < 0 or y >= self.columns:
            return False
        if not self.maze[y][x]:
            return False
        return True

    def validMove(self, x, y, direction):
        """ Verifica se a coordenada x, y pode ser movida para a direção direction """
        x_new, y_new = self.directionCoord(direction, x, y)
        if self.validCoord(x_new, y_new) == False:
            return False
        if len(direction)==1:
            return True
        d1, d2 = list(direction)
        x1, y1 = self.directionCoord(d1, x, y)
        x2, y2 = self.directionCoord(d2, x, y)
        if not self.validCoord(x1, y1) and not self.validCoord(x2, y2):
            return False
        return True

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

    def lee(self, origin):
        """Lee: Busca em largura para encontrar o caminho mais curto a partir de uma coordenada considerando paredes"""
        directionmap = [['P' for x in range(self.columns)] for y in range(self.rows)]
        costmap = [[-1 for x in range(self.columns)] for y in range(self.rows)]

        x_origin, y_origin = origin

        costmap[y_origin][x_origin] = 0
        queue = [{'x':x_origin,'y':y_origin, 'cost':0}]
        
        while queue:
            item = queue.pop(0)
            x = item['x']
            y = item['y']
            cost = item['cost']

            for direction in self.directions:
                x_new, y_new = self.directionCoord(direction, x, y)
                #Se for válido, não foi visitado e não é uma parede
                if self.validMove(x, y, direction) and costmap[y_new][x_new]==-1:
                    costmap[y_new][x_new] = cost + self.action_cost[direction]
                    directionmap[y_new][x_new] = self.oppositeDirection(direction)
                    self.insert_sorted_list(queue, {'x':x_new,'y':y_new, 'cost':costmap[y_new][x_new]})

        return directionmap, costmap
    
    def order_nodes(self, nodes, costs):
        """Ordena os nós de acordo com o custo"""
        nodes_ordered = []
        for node in nodes:
            x, y = node
            nodes_ordered.append({'node':node, 'cost':costs[y][x]})

        nodes_ordered.sort(key=lambda x: x['cost'])
        
        return [node['node'] for node in nodes_ordered]
    

    def makePlan(self, origin:tuple, dest:tuple, directions=None):
        """
        Cria um plano de coordenadas
        @param x: coordenada x
        @param y: coordenada y
        """
        plan = []

        while origin != dest:
            x_dest, y_dest = dest
            direction = directions[y_dest][x_dest]
            plan.insert(0,self.oppositeDirection(direction))
            dest = self.directionCoord(direction, x_dest, y_dest)
            
        return plan
    
    def makePlans(self, origin, nodes, directions):
        """Cria os planos de acordo com as direções"""
        direction_filter = {}

        for dest in nodes:
            direction_filter[dest] = self.makePlan(origin, dest, directions)

        return direction_filter

    def makeCompleteGraph(self):
        """Cria um grafo completo entre agente e vítimas"""

        entities = [(self.x, self.y)]+self.victims
        for origin in entities:
            directions_v, costs_v = self.lee(origin)
            ordered_nodes = self.order_nodes(entities, costs_v)
            plans_v = self.makePlans(origin, ordered_nodes, directions_v)
            self.nearests[origin] = ordered_nodes
            self.plans[origin] = plans_v
            self.visited[origin]=False
            
            for dest in entities:
                x, y = dest
                self.cost[origin, dest] = costs_v[y][x]
                
    def get_rescued(self):
        """Retorna o total de vítimas resgatadas"""
        return self.rescued

    def __str__(self):
        """Retorna informações de posição, tempo, bateria, pacotes e vítimas resgatadas"""
        return f"Socorrista: ({self.x}, {self.y}) | Tempo: {self.time} | Bateria: {self.battery} | Pacotes: {self.packages} | Resgatadas: {self.rescued}"