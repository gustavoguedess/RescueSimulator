
class Block:
    """
    Block: bloco do labirinto
    Armazena a categoria, cor e o ícone do bloco
    """
    color = {
        "blank": (255,255,255),
        "wall": (100,100,100),
        "agentv": (0,200,200),
        "agents": (0,200,0),
        "victim": (200,200,0),
    }
    def __init__(self, x=0, y=0, category="blank"):
        self.x = x
        self.y = y
        self.setCategory(category)
    
    def setCategory(self, category):
        self.category = category
        self.color = Block.color[category]