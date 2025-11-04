import pygame

class Button:
    def __init__(self, pos, image, clicked, scale = 1, locked = False):
        self.width = int(image.get_width() * scale)
        self.height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.image_clicked = pygame.transform.scale(clicked, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.topleft = pos
        self.clicked = False
        self.locked = locked
        
    # Checks for mouse click on button and draws it to the screen
    def draw(self, screen):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 1 and not self.locked:
            screen.blit(self.image_clicked, (self.rect.x, self.rect.y))
            if not self.clicked:
                self.clicked = True
                return True
        else: screen.blit(self.image, (self.rect.x, self.rect.y))
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        return False

class TTT_Tile(Button):
    def __init__(self, pos, image, image_x, image_o, scale=1, locked=False):
        super().__init__(pos, image, image, scale, locked)
        self.image_blank = self.image
        self.image_x = pygame.transform.scale(image_x, (self.width, self.height))
        self.image_o = pygame.transform.scale(image_o, (self.width, self.height))

    def draw(self, screen):
        return super().draw(screen)
    
    def was_clicked(self, screen):
        pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0] == 1 and not self.locked

    def place_human(self):
        self.image = self.image_x
        self.image_clicked = self.image
        self.locked = True
    
    def place_ai(self):
        self.image = self.image_o
        self.image_clicked = self.image
        self.locked = True
    
    def clear(self):
        self.image = self.image_blank
        self.image_clicked = self.image
        self.locked = False