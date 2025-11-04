import pygame

class Rectangle():
    def __init__(self, pos, size, color=(255,255,255)):
        self.pos = pos
        self.rect = pygame.Surface(size)
        self.rect.fill(color)
    
    def draw(self, screen):
        screen.blit(self.rect, self.pos)