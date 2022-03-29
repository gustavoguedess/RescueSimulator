
class Block:
    """
    Block: bloco do labirinto
    Armazena a categoria, cor e o ícone do bloco
    """
    color = {
        "blank": (255,255,255),
        "wall": (100,100,100),
        "agent": (0,200,0),
        "victim": (0,0,200),
    }
    icon = {
        "blank": "_",
        "wall": "X",
        "agent": "A",
        "victim": "V",
    }
    def __init__(self, x=0, y=0, category="blank"):
        self.x = x
        self.y = y
        self.setCategory(category)
    
    def setCategory(self, category):
        self.category = category
        self.color = Block.color[category]
        self.icon = Block.icon[category]