from pkg.block import Block

class AgentL(Block):
    def __init__(self, origin, victims, walls, config):
        x,y = origin
        super().__init__(x, y, "agent")
        self.origin = origin
        self.x = x
        self.y = y 

        self.height = config['maxLin']
        self.width = config['maxCol']

        self.victims = victims
        self.walls = walls
        self.Tl = config['Tl']

        self.directions = ["N", "S", "E", "W" , "NE", "SE", "NW", "SW"]

    def check_wall(self,x,y):
        return (x,y) in self.walls

    def valid_coord(self, x, y):
        return x >= 0 and x < self.width and y >= 0 and y < self.height

    def get_new_coord(self, x, y, direction):
        coord = {'N': (x, y-1), 'S': (x, y+1), 'E': (x+1, y), 'W': (x-1, y), 'NE': (x+1, y-1), 'SE': (x+1, y+1), 'NW': (x-1, y-1), 'SW': (x-1, y+1)}
        return coord[direction]

    def valid_move(self, x, y, direction):
        dest_x, dest_y = self.get_new_coord(x, y, direction)
        
        if not self.valid_coord(dest_x, dest_y):
            return False
        if self.check_wall(dest_x, dest_y):
            return False
        if len(direction)==1:
            return True
        d1, d2 = direction
        x1,y1 = self.get_new_coord(x, y, d1)
        x2,y2 = self.get_new_coord(x, y, d2)
        if self.check_wall(x1, y1) and self.check_wall(x2, y2):
            return False
        return True

    def visit(self, x, y):
        self.visited[y][x] = True

    def dfs(self, x, y):
        self.visit(x,y)
        for direction in self.directions:
            if self.valid_move(x, y, direction):
                new_x, new_y = self.get_new_coord(x, y, direction)
                if not self.visited[new_y][new_x]:
                    self.dfs(new_x, new_y)

    def make_maze(self):
        self.visited = [[False for _ in range(self.width)] for _ in range(self.height)]

        self.dfs(self.x, self.y)

    def get_maze(self):
        return self.visited