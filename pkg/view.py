import pygame
from pygame.locals import *
class View():
    """View implementa a visualização do ambiente.
    """
    def __init__(self, model):
        """Construtor da classe View
        @param model: referência para o modelo do ambiente
        """
        pygame.init()
        
        self.model = model
        
        self.color_white = (255, 255, 255)
        self.color_gray = (200, 200, 200)
        self.color_black = (0, 0, 0)
        
        self.font_size = 15
        self.font = pygame.font.SysFont("dejavusans", self.font_size)
        self.font_block = pygame.font.SysFont("dejavusans", 10)

        self.model_size = 750
        self.footer_size = 20

        self.block_size = self.model_size / self.model.rows
        self.width = self.model.columns * self.block_size
        self.height = self.model.rows * self.block_size+self.footer_size

        self.window = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Rescue Simulator")
        self.surface = pygame.display.get_surface()
        self.window.fill(self.color_white)
        pygame.display.flip()
        pygame.display.update()

        for _ in self.keyboard_event(): pass

    def draw(self, debug=False, pov=None):
        """Desenha o labirinto na tela
        """
        for row in range(self.model.rows):
            for column in range(self.model.columns):
                block = self.model.blocks[row][column]
                self.drawBlock(block, debug, pov)
        
        if pov:
            self.drawBlock(self.model.getAgent())
        
        #draw footer
        self.drawFooter(str(self.model))

        pygame.display.update()

    def drawFooter(self, text):
        """Desenha o rodapé na tela
        @param text: texto a ser desenhado
        """
        pygame.draw.rect(self.surface, self.color_gray, (0, self.height-self.footer_size, self.width, self.footer_size))
        text = self.font.render(text, True, self.color_black)
        self.surface.blit(text, (0, self.model.rows * self.block_size+2), )

    def drawBlock(self, block, debug = False, pov = None):
        """Desenha um bloco na tela
        @param block: bloco a ser desenhado
        """
        #draw text in block
        pygame.draw.rect(self.surface, self.getColorBlock(block, pov), (block.x * self.block_size, block.y * self.block_size, self.block_size, self.block_size))
        
        pygame.draw.rect(self.surface, self.color_black, (block.x * self.block_size, block.y * self.block_size, self.block_size, self.block_size), width=1)

        agent = self.model.agentV
        if agent and debug and pov=='V':
            cost_block_agent = agent.cost_block(block, by='agent')
            if cost_block_agent!=-1:
                text = self.font_block.render(str(cost_block_agent), True, self.getColorBlock(agent))
                self.surface.blit(text, (block.x*self.block_size+1, block.y*self.block_size-1), )
            cost_block_base = agent.cost_block(block, by='base')
            if cost_block_base!=-1:
                text = self.font_block.render(str(cost_block_base), True, self.color_black)
                self.surface.blit(text, (block.x*self.block_size+self.block_size-15, block.y*self.block_size+self.block_size-12), )
         
    def getColorBlock(self, block, pov=None):
        """Retorna a cor de um bloco
        @param block: bloco a ser desenhado
        """
        if pov=='V':
            if self.model.agentV is None:
                return block.color
            if not self.model.agentV.visited[block.y][block.x]: 
                return tuple(c/5 for c in block.color)
        elif pov=='S':
            if self.model.agentS is None:
                return block.color
            if self.model.agentS.maze[block.y][block.x] == 0 : 
                return self.color_black
        return block.color

    def drawSquare(self, x, y, color):
        """Desenha um quadrado na tela
        @param x: posição x do quadrado
        @param y: posição y do quadrado
        @param color: cor do quadrado
        """
        pygame.draw.rect(self.surface, color, (x, y, self.block_size, self.block_size))
        pygame.display.update()
    
    def keyboard_event(self):
        """Retorna eventos de teclado
        """
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    yield "pause"
                elif event.key == pygame.K_q:
                    yield "exit"
                elif event.key == pygame.K_d:
                    yield "debug"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    yield "+"
                if event.key == pygame.K_DOWN:
                    yield "-"
        yield None