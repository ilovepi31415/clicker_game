import json
import math
import pygame


# Info for loading and saving data
filename = 'savefile.json'
data = {  # Defaults
    'score': 0,
    'upgrades_1': [0, 0, 0, 0],
    'points_per_click': 1
}

with open(filename, 'r') as file:
    json_data = json.load(file)
    data.update(json_data)

# Assign JSON values to python variables
score = data['score']
upgrades = data['upgrades_1']
points_per_click = data['points_per_click']

class Button:
    def __init__(self, x, y, image, clicked, scale = 1):
        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.image_clicked = pygame.transform.scale(clicked, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self):
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
    small = int(n / (1000 ** orders_of_magnitude) * 10) / 10
    if orders_of_magnitude < len(symbols):
        return str(small) + symbols[orders_of_magnitude]
    else: return str(small) + 'e' + str(orders_of_magnitude * 3)


# Pygame initialization
pygame.init()
screen = pygame.display.set_mode((800, 500))
pygame.display.set_caption('Clicker Game v0.1')
pixel_font = pygame.font.Font('pixelType.ttf', 50)
clock = pygame.time.Clock()

main_button = Button(70, 200, pygame.image.load('icons/score_button.png').convert_alpha(), pygame.image.load(
    'icons/score_clicked.png').convert_alpha(), 10)
clear_button = Button(500, 200, pygame.image.load('icons/clear_button.png').convert_alpha(), pygame.image.load(
    'icons/clear_clicked.png').convert_alpha(), 5)
upgrade_button = Button(500, 100, pygame.image.load('icons/upgrade_button.png').convert_alpha(), pygame.image.load(
    'icons/upgrade_clicked.png').convert_alpha(), 5)


# Game Loop goes here
run = True
while run:
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    if main_button.draw():
        score += points_per_click
    if clear_button.draw():
        score = 0
        points_per_click = 1
        upgrades = [0, 0, 0, 0]
    if upgrade_button.draw():
        price = get_price(1)
        if price <= score:
            score -= price
            upgrades[0] += 1
            points_per_click += 1

    score_surf = pixel_font.render(f'Score: {format_big_number(score)}', False, (255, 255, 255))
    score_rect = score_surf.get_rect(center=(400, 350))
    screen.blit(score_surf, score_rect)

    price_surf = pixel_font.render(f'Price: {format_big_number(get_price(1))}', False, (255, 255, 255))
    price_rect = price_surf.get_rect(center=(400, 250))
    screen.blit(price_surf, price_rect)

    pygame.display.update()
    clock.tick(60)

pygame.quit()

data['score'] = score
data['upgrades_1'] = upgrades
data['points_per_click'] = points_per_click

with open(filename, 'w') as file:
    json.dump(data, file)
