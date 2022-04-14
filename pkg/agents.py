from block import Block

class AgentS(Block):
    """
    AgentV: Agente Vasculhador 
    """

    def __init__(self, x, y, rows, columns, Bs, Ks):
        super().__init__(x, y, "agents")
        self.x_base = x
        self.y_base = y
        self.rows = rows
        self.columns = columns
        self.Bs = Bs
        self.Ks = Ks

        self.plan = []

    def deliberate(self):
        if not self.plan:
            return False

        self.x, self.y = self.plan.pop(0)
        print("Agente socorrista delibera: ", self.x, self.y)

        return True

    def makePlan(self, Victims):
        """Cria um plano para o agente
        @param Victims: lista de vítimas
        """
        self.plan = []
        for victim in Victims:
            x, y = victim
            self.plan.append((x, y))
        self.plan.append((self.x_base, self.y_base))

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