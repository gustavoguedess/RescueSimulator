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
        
        self.font_size = 20
        self.font = pygame.font.SysFont("dejavusans", self.font_size)

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

    def draw(self):
        """Desenha o labirinto na tela
        """
        """
        print("Labirinto:")
        for row in range(self.model.rows):
            for column in range(self.model.columns):
                print("*", end="")
            print("")
        """
        for row in range(self.model.rows):
            for column in range(self.model.columns):
                block = self.model.blocks[row][column]
                self.drawBlock(block)
        
        self.drawBlock(self.model.agent)
        #draw footer
        self.drawFooter("Rescue Simulator")

        pygame.display.update()

    def drawFooter(self, text):
        """Desenha o rodapé na tela
        @param text: texto a ser desenhado
        """
        pygame.draw.rect(self.surface, self.color_gray, (0, self.height-self.footer_size, self.width, self.footer_size))
        text = self.font.render(text, True, self.color_black)
        self.surface.blit(text, (0, self.model.rows * self.block_size), )

    def drawBlock(self, block):
        """Desenha um bloco na tela
        @param block: bloco a ser desenhado
        """
        pygame.draw.rect(self.surface, block.color, (block.x * self.block_size, block.y * self.block_size, self.block_size, self.block_size))
         
    def drawSquare(self, x, y, color):
        """Desenha um quadrado na tela
        @param x: posição x do quadrado
        @param y: posição y do quadrado
        @param color: cor do quadrado
        """
        pygame.draw.rect(self.surface, color, (x, y, self.block_size, self.block_size))
        pygame.display.update()
    