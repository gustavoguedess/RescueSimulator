from pkg.block import Block

class AgentS(Block):
    """
    AgentV: Agente Vasculhador 
    """

    def __init__(self, origin, victims, vitals, difficult, config):
        x,y = origin
        super().__init__(x, y, "agents")
        self.base_x = x
        self.base_y = y
        self.origin = origin

        self.rows = config['maxLin']
        self.columns = config['maxCol']

        self.victims = victims
        self.vitals = self.map_vitals(vitals)
        self.difficult = self.map_difficult(difficult)

        self.Ts = config['Ts']
        self.Ks = config['Ks']

        self.directions = ['N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW']
        self.direction_cost = {
            'N': 1, 'S': 1, 'E': 1, 'W': 1, 
            'NE': 1.5, 'NW': 1.5, 'SE': 1.5, 'SW': 1.5}

    def map_vitals(self, vitals):
        new_vitals = {}
        for i in range(len(vitals)):
            new_vitals[self.victims[i]] = vitals[i][-1]
        return new_vitals 
    
    def map_difficult(self, difficult):
        new_difficult = {}
        for i in range(len(difficult)):
            new_difficult[self.victims[i]] = difficult[i][-1]
        return new_difficult

    def print_victims(self):
        print("Vitals:")

        print(f"Victim\tVital\tDifficult")
        for i in range(len(self.victims)):
            print(f"{self.victims[i]} \t {self.vitals[self.victims[i]]} \t {self.difficult[self.victims[i]]}")
        print()
