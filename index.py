import json
import math
import pygame
from random import randint
from button import Button, TTT_Tile
from rectangle import Rectangle
from tictactoe import GameBoard

# Info for loading and saving data
filename = 'savefile.json'
data = {  # Defaults
    'score': 0,
    'upgrades': [0, 0, 0, 0],
    'upgrade_unlocks' : [True, True, True, True],
    'game_phase': 1,
}

try:
    with open(filename, 'r') as file:
        json_data = json.load(file)
        data.update(json_data)
except FileNotFoundError:
    pass

# Assign JSON values to python variables
score = data['score']
upgrades = data['upgrades']
unlocks = data['upgrade_unlocks']
points_per_click = upgrades[0] + 1
points_per_second = upgrades[1]
crit_chance = upgrades[2]
game_phase = data['game_phase']

# Allows easy setting of window sizes
window_sizes_by_phase = {
    1: (800, 350),
    2: (1200, 350),
}

# Class for the upgrade buttons
class Upgrade(Button):
    def __init__(self, id, pos, image, clicked, title, scale = 1, locked = True):
        super().__init__(pos, image, clicked, scale, locked)
        self.locked_image = pygame.image.load('icons/button_locked.png')
        self.width = int(self.locked_image.get_width() * scale)
        self.height = int(self.locked_image.get_height() * scale)
        self.locked_image = pygame.transform.scale(self.locked_image, (self.width, self.height))
        self.title = title
        self.locked = locked
        self.x = pos[0]
        self.y = pos[1]
        self.id = id

    def draw(self, screen):
        title_surf = body_font.render(self.title, False, (255, 255, 255))
        title_rect = title_surf.get_rect(topleft=(self.x + self.width + 20, self.y + 5))
        screen.blit(title_surf, title_rect)
        price_surf = sub_font.render(f'Price: $ {format_big_number(get_price(self.id))}', False, (255, 255, 255))
        price_rect = price_surf.get_rect(topleft=(self.x + self.width + 20, self.y + 30))
        screen.blit(price_surf, price_rect)
        if not self.locked:
            return super().draw(screen)
        else:
            screen.blit(self.locked_image, (self.rect.x, self.rect.y))

# Still needs a lot of work
class Number_Graphic(pygame.sprite.Sprite):
    def __init__(self, n, pos, width, height, crit):
        super().__init__()
        self.n = n
        self.x = randint(pos[0], pos[0] + width)
        self.y = randint(pos[1], pos[1] + height)
        self.opacity = 255
        self.color = (255, 255, 255) if crit == 1 else (200, 200, 0) if crit == 2 else (0, 200, 200)
        self.crit = crit

    def update(self):
        graphic_surf = body_font.render(f'$ {format_big_number(self.n)}', False, self.color) if self.crit == 1 else title_font.render(f'$ {format_big_number(self.n)}', False, self.color)
        graphic_surf.set_alpha(self.opacity)
        graphic_rect = graphic_surf.get_rect(center=(self.x, self.y))
        graphic_rect.width
        screen.blit(graphic_surf, graphic_rect)
        self.opacity = (self.opacity / 1.05) - 1
        self.destroy()

    def destroy(self):
        if self.opacity <= 0:
            self.kill()

def check_crit(chance):
    benchmark = randint(1, 100)
    return 1 if chance < benchmark else int((chance - benchmark) /100) + 2

def exp_price(tier):
    level = upgrades[tier - 1]
    early_base = tier + 1
    late_base = 1 + (tier + 1) / 10

    if level < 6:
        price = early_base ** level
    else:
        price = int(1.2 ** level) + (early_base ** 5) * (level - 4)
    return price

def get_price(tier):
    level = upgrades[tier - 1] + 1
    exp = tier + 1
    return  (level ** 2) + level * tier

def format_big_number(n):
    if n < 1000: return n
    symbols = ['', 'K', 'M', 'B', 'T', 'q', 'Q', 's', 'S', 'O', 'N', 'd', 'Ud', 'Dd', 'Td', 'qd', 'Qd', 'sd', 'Sd', 'Od', 'Nd', 'V']
    orders_of_magnitude = int(math.log(n, 10) / 3)
    small = int(n / (1000 ** orders_of_magnitude) * 100) / 100
    if orders_of_magnitude < len(symbols):
        return str(small) + symbols[orders_of_magnitude]
    else: return str(small) + 'e' + str(orders_of_magnitude * 3)

def update_window_size():
    return pygame.display.set_mode(window_sizes_by_phase[game_phase])

# Pygame initialization
pygame.init()
screen = update_window_size()
pygame.display.set_caption('Clicker Game v0.2')
title_font = pygame.font.Font('pixelType.ttf', 70)
body_font = pygame.font.Font('pixelType.ttf', 40)
sub_font = pygame.font.Font('pixelType.ttf', 25)

clock = pygame.time.Clock()

# Phase 1 Buttons
main_button = Button((70, 150), pygame.image.load('icons/score_button.png').convert_alpha(), pygame.image.load(
    'icons/score_clicked.png').convert_alpha(), 10)
clear_button = Button((0, 0), pygame.image.load('icons/clear_button.png').convert_alpha(), pygame.image.load(
    'icons/clear_clicked.png').convert_alpha(), 5)
upgrade_click_power = Upgrade(1, (500, 50), pygame.image.load('icons/upgrade_button.png').convert_alpha(), pygame.image.load(
    'icons/upgrade_clicked.png').convert_alpha(), '+$1 / click', 5, unlocks[0])
upgrade_passive_income = Upgrade(2, (500, 125), pygame.image.load('icons/upgrade_button.png').convert_alpha(), pygame.image.load(
    'icons/upgrade_clicked.png').convert_alpha(), '+$1 / second', 5, unlocks[1])
upgrade_crit_chance = Upgrade(3, (500, 200), pygame.image.load('icons/upgrade_button.png').convert_alpha(), pygame.image.load(
    'icons/upgrade_clicked.png').convert_alpha(), '+1% crit chance', 5, unlocks[2])
click_graphic_group = pygame.sprite.Group()

passive_income_timer = pygame.USEREVENT + 1
pygame.time.set_timer(passive_income_timer, 1000)

# Phase 2 Buttons
ttt_buttons: list[TTT_Tile] = []
for i in range(9):
    tile = TTT_Tile((875 + (100 * (i % 3)), 50 + (100 * (i // 3))), pygame.image.load('icons/tic_tac_toe_blank.png').convert_alpha(), pygame.image.load('icons/tic_tac_toe_x.png').convert_alpha(), pygame.image.load('icons/tic_tac_toe_o.png').convert_alpha(), 10)
    ttt_buttons.append(tile)
ttt_bars = []
for i in range(2):
    h_bar = Rectangle((850, 25 + 100 * (i + 1) - 3), (300, 6))
    v_bar = Rectangle((850 + 100 * (i + 1) - 3, 25), (6, 300))
    ttt_bars.append(h_bar)
    ttt_bars.append(v_bar)
board = GameBoard()

# Game Loop goes here --------------------------------------------------------------------------------------------------
run = True
while run:
    # Check game phase
    if game_phase == 1 and score >= 10000:
        game_phase = 2
        screen = update_window_size()
    
    screen.fill((0, 0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == passive_income_timer:
            score += points_per_second

    if main_button.draw(screen):
        # Creates the small graphic on the button and adds the money to the user's total
        crit_mult =  check_crit(crit_chance)
        added_points = points_per_click * crit_mult
        score += added_points
        click_graphic_group.add(Number_Graphic(added_points, main_button.rect.topleft, main_button.width, main_button.height, crit_mult))
    if clear_button.draw(screen):
        # Resets all values to the defaults as if the user opened a fresh copy
        score = 0
        points_per_click = 1
        points_per_second = 0
        crit_chance = 0
        upgrades = [0, 0, 0, 0]
        unlocks = [True, True, True, True]
        game_phase = 1
        update_window_size()

    # Attempts to purchase an upgrade if a button is clicked
    if upgrade_click_power.draw(screen):
        price = get_price(upgrade_click_power.id)
        if price <= score:
            score -= price
            upgrades[0] += 1
            points_per_click += 1
    if upgrade_passive_income.draw(screen):
        price = get_price(upgrade_passive_income.id)
        if price <=  score:
            score -= price
            upgrades[1] += 1
            points_per_second += 1
    if upgrade_crit_chance.draw(screen):
        price = get_price(upgrade_crit_chance.id)
        if price <=  score:
            score -= price
            upgrades[2] += 1
            crit_chance += 1
    
    # Unlocking checks for the various upgrades
    if score >= 10 and upgrade_click_power.locked:
        unlocks[0] = False
    if score >= 10 ** 2 and upgrade_passive_income.locked:
        unlocks[1] = False
    if score >= 10 ** 3 and upgrade_crit_chance.locked:
        unlocks[2] = False
    upgrade_click_power.locked = unlocks[0]
    upgrade_passive_income.locked = unlocks[1]
    upgrade_crit_chance.locked = unlocks[2]

    # Updates the fading of all graphics
    click_graphic_group.update()

    # Graphic of the user's total score
    score_surf = title_font.render(f'$ {format_big_number(score)}', False, (255, 255, 255))
    score_rect = score_surf.get_rect(center=(400, 300))
    screen.blit(score_surf, score_rect)

    if game_phase > 1:
        rect = pygame.Surface((10, 350))
        rect.fill((255, 255, 255))
        screen.blit(rect, (800, 0))

        # Handle Tic-Tac-Toe logic
        for i in range(len(ttt_buttons)):
            tile = ttt_buttons[i]
            # Write AI moves to screen
            if board.state[i] == 2 and not tile.locked:
                tile.place_ai()
            if board.state[i] == 0 and tile.locked:
                tile.clear()
            if board.check_winner(1):
                board = GameBoard()
            if board.check_winner(2):
                board = GameBoard()
            if tile.draw(screen):
                tile.place_human()
                board.move_human(i)
                if board.check_cat():
                    board = GameBoard()
                else:
                    board.move_ai_good()
        for bar in ttt_bars:
            bar.draw(screen)        

    pygame.display.update()
    clock.tick(60)
# ----------------------------------------------------------------------------------------------------------------------
pygame.quit()

data['score'] = score
data['upgrades'] = upgrades
data['upgrade_unlocks'] = unlocks
data['game_phase'] = game_phase

with open(filename, 'w') as file:
    json.dump(data, file)
