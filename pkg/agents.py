from block import Block

class AgentS(Block):
    """
    AgentV: Agente Vasculhador 
    """

    def __init__(self, x, y, rows, columns, Bs, Ks):
        super().__init__(x, y, "agents")
        self.base_x = x
        self.base_y = y
        self.rows = rows
        self.columns = columns
        self.Bs = Bs
        self.Ks = Ks

        self.directions = ["N", "S", "E", "W" , "NE", "SE", "NW", "SW"]
        self.action_cost = {
            "N": 1, "S": 1, "E": 1, "W": 1,
            "NE": 1.5, "SE": 1.5, "NW": 1.5, "SW": 1.5
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
        """
        self.plan = []
        self.rescued = 0

    def deliberate(self):
        if not self.plan:
            origin = (self.x, self.y)
            
            while True:
                if not self.cost[origin]:
                    entity = (self.base_x, self.base_y)
                    break
                cost = self.cost[origin].pop(0)
                entity = cost['destination']
                
                if not self.visited[entity]:
                    self.visited[entity] = True
                    break

            self.plan = self.plans[origin][entity]

        if not self.plan:
            return False
        
        action = self.plan.pop(0)
        if action in self.directions:
            self.move(action)

        return True

    def move(self, direction):
        self.x, self.y = self.directionCoord(direction, self.x, self.y)
        if (self.x, self.y) in self.victims:
            self.rescued += 1
            self.victims.remove((self.x, self.y))

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

    def lee(self, x_origin, y_origin):
        """Lee: Busca em largura para encontrar o caminho mais curto a partir de uma coordenada considerando paredes"""
        directionmap = [['P' for x in range(self.columns)] for y in range(self.rows)]
        costmap = [[-1 for x in range(self.columns)] for y in range(self.rows)]
    
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

        costmap_filter = []
        direction_filter = {}

        direction_filter[(self.base_x, self.base_y)] = self.makePlan((x_origin, y_origin), (self.base_x, self.base_y), directionmap)
        for victim in self.victims:
            x, y = victim
            self.insert_sorted_list(costmap_filter, {'destination':victim, 'cost':costmap[y][x]})
            direction_filter[(x, y)] = self.makePlan((x_origin, y_origin), (x, y), directionmap)

        return costmap_filter, direction_filter

    def makePlan(self, origin:tuple, dest:tuple, directions=None):
        """
        Cria um plano de coordenadas
        @param x: coordenada x
        @param y: coordenada y
        """
        x_origin, y_origin = origin
        x_dest, y_dest = dest

        plan = []

        while not (x_origin == x_dest and y_origin == y_dest):
            direction = directions[y_dest][x_dest]
            plan.insert(0,self.oppositeDirection(direction))
            x_dest, y_dest = self.directionCoord(direction, x_dest, y_dest)
            
        return plan
    
    def makeCompleteGraph(self):
        """Cria um grafo completo entre agente e vítimas"""
        self.cost = {}
        self.plans = {}
        self.visited = {}

        entities = [(self.x, self.y)]+self.victims
        for entity in entities:
            x, y = entity
            cost_v, plans_v = self.lee(x, y)
            self.cost[entity] = cost_v
            self.plans[entity] = plans_v
            self.visited[entity]=False
        

    def makeSpanningTree(self):
        """Cria uma árvore mínima"""
        fila = []
        
        entities = [(self.x, self.y)]+self.victims
        for entity in entities:
            costs = self.cost[entity]
            for ent,cost in costs.items():
                item = {'ent':ent, 'cost':cost}
                self.insert_sorted_list(fila, item)
    def get_rescued(self):
        """Retorna o total de vítimas resgatadas"""
        return self.rescued