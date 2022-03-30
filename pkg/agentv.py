from block import Block

class AgentV(Block):
    """
    AgentV: Agente Vasculhador 
    """

    def __init__(self, x, y):
        super().__init__(x, y, "agent")

    def move(self, direction):
        if direction == "N":
            self.y -= 1
        elif direction == "S":
            self.y += 1
        elif direction == "E":
            self.x += 1
        elif direction == "W":
            self.x -= 1

    def deliberate(self):
        self.move("E")
        return 0