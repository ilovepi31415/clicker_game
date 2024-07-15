import json
import math
import pygame
from random import randint


# Info for loading and saving data
filename = 'savefile.json'
data = {  # Defaults
    'score': 0,
    'upgrades': [0, 0, 0, 0],
    'upgrade_unlocks' : [True, True, True, True],
    'points_per_click': 1
}

with open(filename, 'r') as file:
    json_data = json.load(file)
    data.update(json_data)

# Assign JSON values to python variables
score = data['score']
upgrades = data['upgrades']
points_per_click = data['points_per_click']
unlocks = data['upgrade_unlocks']

class Button:
    def __init__(self, x, y, image, clicked, scale = 1):
        self.width = int(image.get_width() * scale)
        self.height = int(image.get_height() * scale)
        self.image = pygame.transform.scale(image, (self.width, self.height))
        self.image_clicked = pygame.transform.scale(clicked, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self): # Checks for mouse click on button and draws it to the screen
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


class Upgrade(Button):
    def __init__(self, id, x, y, image, clicked, title, price, scale = 1, locked = True):
        super().__init__(x, y, image, clicked, scale)
        self.locked_image = pygame.image.load('icons/button_locked.png')
        self.width = int(self.locked_image.get_width() * scale)
        self.height = int(self.locked_image.get_height() * scale)
        self.locked_image = pygame.transform.scale(self.locked_image, (self.width, self.height))
        self.title = title
        self.price = price
        self.locked = locked

    def draw(self):

        if not self.locked:
            return super().draw()
        else:
            screen.blit(self.locked_image, (self.rect.x, self.rect.y))

#Still needs a lot of work
class Number_Graphic(pygame.sprite.Sprite):
    def __init__(self, n, pos, width, height):
        super().__init__()
        self.n = n
        self.x = randint(pos[0], pos[0] + width)
        self.y = randint(pos[1], pos[1] + height)
        self.opacity = 255

    def update(self):
        graphic_surf = body_font.render(f'$ {format_big_number(self.n)}', False, (255, 255, 255))
        graphic_surf.set_alpha(self.opacity)
        graphic_rect = graphic_surf.get_rect(center=(self.x, self.y))
        graphic_rect.width
        screen.blit(graphic_surf, graphic_rect)
        self.opacity = (self.opacity / 1.05) - 1
        self.destroy()

    def destroy(self):
        if self.opacity <= 0:
            self.kill()


def get_price(tier):
    level = upgrades[tier - 1]
    if level < 6:
        price = 2 ** level
    else:
        price = int(1.2 ** level) + 32 * (level - 4)
    return price

def format_big_number(n):
    if n < 1000: return n
    symbols = ['', 'K', 'M', 'B', 'T', 'q', 'Q', 's', 'S', 'O', 'N', 'd', 'Ud', 'Dd', 'Td', 'qd', 'Qd', 'sd', 'Sd', 'Od', 'Nd', 'V']
    orders_of_magnitude = int(math.log(n, 10) / 3)
    small = int(n / (1000 ** orders_of_magnitude) * 100) / 100
    if orders_of_magnitude < len(symbols):
        return str(small) + symbols[orders_of_magnitude]
    else: return str(small) + 'e' + str(orders_of_magnitude * 3)

def number_graphic(n, pos, width, height):
    score_surf = body_font.render(f'$ {format_big_number(n)}', False, (255, 255, 255))
    score_rect = score_surf.get_rect(center=(pos[0] + randint(0, width), pos[1] + randint(0, height)))
    screen.blit(score_surf, score_rect)


# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((800, 500))
pygame.display.set_caption('Clicker Game v0.1')
title_font = pygame.font.Font('pixelType.ttf', 70)
body_font = pygame.font.Font('pixelType.ttf', 40)
clock = pygame.time.Clock()

main_button = Button(70, 200, pygame.image.load('icons/score_button.png').convert_alpha(), pygame.image.load(
    'icons/score_clicked.png').convert_alpha(), 10)
clear_button = Button(500, 200, pygame.image.load('icons/clear_button.png').convert_alpha(), pygame.image.load(
    'icons/clear_clicked.png').convert_alpha(), 5)
upgrade_button = Upgrade(1, 500, 100, pygame.image.load('icons/upgrade_button.png').convert_alpha(), pygame.image.load(
    'icons/upgrade_clicked.png').convert_alpha(), 'hi', 2, 5, unlocks[0])

click_graphic_group = pygame.sprite.Group()

# Game Loop goes here --------------------------------------------------------------------------------------------------
run = True
while run:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if main_button.draw():
        score += points_per_click
        click_graphic_group.add(Number_Graphic(points_per_click, main_button.rect.topleft, main_button.width, main_button.height))
        # number_graphic(points_per_click, main_button.rect.topleft, main_button.width, main_button.height)
    if clear_button.draw():
        score = 0
        points_per_click = 1
        upgrades = [0, 0, 0, 0]
        unlocks = [True, True, True, True]
    if upgrade_button.draw():
        price = get_price(1)
        if price <= score:
            score -= price
            upgrades[0] += 1
            points_per_click += 1
    if score >= 10 and upgrade_button.locked:
        unlocks[0] = False
    upgrade_button.locked = unlocks[0]

    click_graphic_group.update()

    score_surf = title_font.render(f'$ {format_big_number(score)}', False, (255, 255, 255))
    score_rect = score_surf.get_rect(center=(400, 350))
    screen.blit(score_surf, score_rect)

    price_surf = body_font.render(f'Price: $ {format_big_number(get_price(1))}', False, (255, 255, 255))
    price_rect = price_surf.get_rect(center=(400, 250))
    screen.blit(price_surf, price_rect)

    pygame.display.update()
    clock.tick(60)
# ----------------------------------------------------------------------------------------------------------------------
pygame.quit()

data['score'] = score
data['upgrades'] = upgrades
data['points_per_click'] = points_per_click
data['upgrade_unlocks'] = unlocks

with open(filename, 'w') as file:
    json.dump(data, file)
