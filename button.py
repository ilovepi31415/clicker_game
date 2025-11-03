import pygame

class Button:
    def __init__(self, pos, image, clicked, scale = 1):
        self.width = int(image.get_width() * scale)
        self.height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.image_clicked = pygame.transform.scale(clicked, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.clicked = False

    # Checks for mouse click on button and draws it to the screen
    def draw(self, screen):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 1:
            screen.blit(self.image_clicked, (self.rect.x, self.rect.y))
            if not self.clicked:
                self.clicked = True
                return True
        else: screen.blit(self.image, (self.rect.x, self.rect.y))
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        return False
