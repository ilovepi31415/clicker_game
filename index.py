import json
import math
import pygame
from random import randint
from button import Button, TTT_Tile
from rectangle import Rectangle
from tictactoe import GameBoard
from math_quiz import Quiz

# Info for loading and saving data
filename = 'savefile.json'
data = {  # Defaults
    'score': 0,
    'wins': 0,
    'iq': 0,
    'upgrades': [0] * 7,
    'upgrade_unlocks': [True] * 7,
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
wins = data['wins']
iq = data['iq']
upgrades = data['upgrades']
unlocks = data['upgrade_unlocks']
points_per_click = upgrades[0] + 1
points_per_second = upgrades[1]
crit_chance = upgrades[2]
ttt_cooldown = 10 - upgrades[3]
money_per_win = upgrades[4] + 1
wins_per_game = upgrades[5] + 1
score_multiplier = upgrades[6] + 1
game_phase = data['game_phase']

# Allows easy setting of window sizes
window_sizes_by_phase = {
    1: (800, 350),
    2: (1450, 350),
    3: (1450, 800),
    4: (2000, 800)
}


# Class for the upgrade buttons
class Upgrade(Button):
    def __init__(
        self, id, pos, image, clicked, title,
        currency, scale=1, locked=True
    ):
        super().__init__(pos, image, clicked, scale, locked)
        self.locked_image = pygame.image.load('icons/button_locked.png')
        self.width = int(self.locked_image.get_width() * scale)
        self.height = int(self.locked_image.get_height() * scale)
        self.locked_image = pygame.transform.scale(
            self.locked_image, (self.width, self.height))
        self.title = title
        self.locked = locked
        self.x = pos[0]
        self.y = pos[1]
        self.id = id
        self.currency = currency

    def draw(self, screen):
        title_surf = body_font.render(self.title, False, (255, 255, 255))
        title_rect = title_surf.get_rect(
            topleft=(self.x + self.width + 20, self.y + 5))
        screen.blit(title_surf, title_rect)
        match(self.currency):
            case 'score':
                price = f'Price: $ {format_big_number(
                    get_quadratic_price(self.id))}'
            case 'wins':
                price = f'Price: {format_big_number(
                    get_linear_price(self.id))} wins'
            case 'iq':
                price = f'Price: {format_big_number(
                    get_quadratic_price(self.id))} IQ'
        price_surf = sub_font.render(price, False, (255, 255, 255))
        price_rect = price_surf.get_rect(
            topleft=(self.x + self.width + 20, self.y + 30))
        screen.blit(price_surf, price_rect)
        if not self.locked:
            return super().draw(screen)
        else:
            screen.blit(self.locked_image, (self.rect.x, self.rect.y))

# The number that pops up


class Number_Graphic(pygame.sprite.Sprite):
    def __init__(self, n, pos, width, height, crit):
        super().__init__()
        self.n = n
        self.x = randint(pos[0], pos[0] + width)
        self.y = randint(pos[1], pos[1] + height)
        self.opacity = 255
        self.color = (255, 255, 255) if crit == 1 else (
            200, 200, 0) if crit == 2 else (0, 200, 200)
        self.crit = crit

    def update(self):
        graphic_surf = body_font.render(f'$ {format_big_number(self.n)}', False, self.color) if self.crit == 1 else title_font.render(
            f'$ {format_big_number(self.n)}', False, self.color)
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
    return 1 if chance < benchmark else int((chance - benchmark) / 100) + 2


def exp_price(tier):
    level = upgrades[tier - 1]
    early_base = tier + 1
    late_base = 1 + (tier + 1) / 10

    if level < 6:
        price = early_base ** level
    else:
        price = int(1.2 ** level) + (early_base ** 5) * (level - 4)
    return price


def get_quadratic_price(tier):
    level = upgrades[tier - 1] + 1
    return (level ** 2) + level * tier


def get_linear_price(tier):
    level = upgrades[tier - 1] + 1
    return level * max(tier - 3, 1)


def format_big_number(n):
    if n < 1000:
        return n
    symbols = ['', 'K', 'M', 'B', 'T', 'q', 'Q', 's', 'S', 'O', 'N',
               'd', 'Ud', 'Dd', 'Td', 'qd', 'Qd', 'sd', 'Sd', 'Od', 'Nd', 'V']
    orders_of_magnitude = int(math.log(n, 10) / 3)
    small = int(n / (1000 ** orders_of_magnitude) * 100) / 100
    if orders_of_magnitude < len(symbols):
        return str(small) + symbols[orders_of_magnitude]
    else:
        return str(small) + 'e' + str(orders_of_magnitude * 3)


def update_window_size():
    return pygame.display.set_mode(window_sizes_by_phase[game_phase])


# Pygame initialization
pygame.init()
screen = update_window_size()
pygame.display.set_caption('Clicker Game v0.4')
giant_font = pygame.font.Font('pixelType.ttf', 200)
math_font = pygame.font.Font('pixelType.ttf', 150)
title_font = pygame.font.Font('pixelType.ttf', 70)
body_font = pygame.font.Font('pixelType.ttf', 40)
sub_font = pygame.font.Font('pixelType.ttf', 25)

clock = pygame.time.Clock()
goals_values = [10, 100, 1000, 10000, 250000, 1000000, float("inf")]
goal_value_index = 0

# Phase 1 Buttons
main_button = Button((70, 150), pygame.image.load('icons/score_button.png').convert_alpha(), pygame.image.load(
    'icons/score_clicked.png').convert_alpha(), 10)
clear_button = Button((305, 100), pygame.image.load('icons/clear_button.png').convert_alpha(), pygame.image.load(
    'icons/clear_clicked.png').convert_alpha(), 5)
upgrade_click_power = Upgrade(1, (500, 50), pygame.image.load('icons/upgrade_button.png').convert_alpha(), pygame.image.load(
    'icons/upgrade_clicked.png').convert_alpha(), '+$1 / click', 'score', 5, unlocks[0])
upgrade_passive_income = Upgrade(2, (500, 125), pygame.image.load('icons/upgrade_button.png').convert_alpha(), pygame.image.load(
    'icons/upgrade_clicked.png').convert_alpha(), '+$1 / second', 'score', 5, unlocks[1])
upgrade_crit_chance = Upgrade(3, (500, 200), pygame.image.load('icons/upgrade_button.png').convert_alpha(), pygame.image.load(
    'icons/upgrade_clicked.png').convert_alpha(), '+1% crit chance', 'score', 5, unlocks[2])
click_graphic_group = pygame.sprite.Group()

passive_income_timer = pygame.USEREVENT + 1
pygame.time.set_timer(passive_income_timer, 1000)

# Phase 2 Buttons
ttt_buttons: list[TTT_Tile] = []
for i in range(9):
    tile = TTT_Tile((875 + (100 * (i % 3)), 50 + (100 * (i // 3))), pygame.image.load('icons/tic_tac_toe_blank.png').convert_alpha(),
                    pygame.image.load('icons/tic_tac_toe_x.png').convert_alpha(), pygame.image.load('icons/tic_tac_toe_o.png').convert_alpha(), 10)
    ttt_buttons.append(tile)
ttt_bars = []
for i in range(2):
    h_bar = Rectangle((850, 25 + 100 * (i + 1) - 3), (300, 6))
    v_bar = Rectangle((850 + 100 * (i + 1) - 3, 25), (6, 300))
    ttt_bars.append(h_bar)
    ttt_bars.append(v_bar)
board = GameBoard()
cooldown = None
upgrade_ttt_timer = Upgrade(4, (1200, 50), pygame.image.load('icons/upgrade_button.png').convert_alpha(
), pygame.image.load('icons/upgrade_clicked.png').convert_alpha(), '-1s / game', 'wins', 5, upgrades[3])
upgrade_ttt_power = Upgrade(5, (1200, 125), pygame.image.load('icons/upgrade_button.png').convert_alpha(
), pygame.image.load('icons/upgrade_clicked.png').convert_alpha(), '+$1000 / win', 'wins', 5, upgrades[4])

# Phase 3 Buttons
quiz = Quiz()
option_1 = Button((60, 550), pygame.image.load(
    'icons/outline_button.png').convert_alpha(), pygame.image.load('icons/outline_clicked.png'), 10)
option_2 = Button((360, 550), pygame.image.load(
    'icons/outline_button.png').convert_alpha(), pygame.image.load('icons/outline_clicked.png'), 10)
option_3 = Button((660, 550), pygame.image.load(
    'icons/outline_button.png').convert_alpha(), pygame.image.load('icons/outline_clicked.png'), 10)
upgrade_math_power = Upgrade(6, (1200, 500), pygame.image.load('icons/upgrade_button.png').convert_alpha(
), pygame.image.load('icons/upgrade_clicked.png').convert_alpha(), '+1 win / win', 'iq', 5, upgrades[5])
upgrade_score_multiplier = Upgrade(7, (1200, 575), pygame.image.load('icons/upgrade_button.png').convert_alpha(
), pygame.image.load('icons/upgrade_clicked.png').convert_alpha(), '+1 Score Mult', 'iq', 6, upgrades[6])

trophy_scale = 20
trophy_surf = pygame.transform.scale(pygame.image.load(
    'icons/trophy.png').convert_alpha(), (20 * trophy_scale, 20 * trophy_scale))
trophy_rect = trophy_surf.get_rect()
trophy_rect.topleft = (1525, 400)

# Game Loop goes here --------------------------------------------------------------------------------------------------
run = True
try:
    while run:
        # Check game phase
        if game_phase == 1 and score >= 10000:
            game_phase = 2
            screen = update_window_size()
        if game_phase == 2 and score >= 250000:
            game_phase = 3
            screen = update_window_size()
        if game_phase == 3 and score >= 1000000:
            game_phase = 4
            screen = update_window_size()

        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == passive_income_timer:
                score += points_per_second

        if main_button.draw(screen):
            # Creates the small graphic on the button and adds the money to the user's total
            crit_mult = check_crit(crit_chance)
            added_points = points_per_click * crit_mult * score_multiplier
            score += added_points
            click_graphic_group.add(Number_Graphic(
                added_points, main_button.rect.topleft, main_button.width, main_button.height, crit_mult))

        if clear_button.draw(screen):
            # Resets all values to the defaults as if the user opened a fresh copy
            score = 0
            points_per_click = 1
            points_per_second = 0
            crit_chance = 0
            upgrades = [0] * 7
            unlocks = [True] * 7
            game_phase = 1
            wins = 0
            iq = 0
            ttt_cooldown = 10
            wins_per_game = 1
            update_window_size()

        # Attempts to purchase an upgrade if a button is clicked
        if upgrade_click_power.draw(screen):
            price = get_quadratic_price(upgrade_click_power.id)
            if price <= score:
                score -= price
                upgrades[0] += 1
                points_per_click += 1
        if upgrade_passive_income.draw(screen):
            price = get_quadratic_price(upgrade_passive_income.id)
            if price <= score:
                score -= price
                upgrades[1] += 1
                points_per_second += 1
        if upgrade_crit_chance.draw(screen):
            price = get_quadratic_price(upgrade_crit_chance.id)
            if price <= score:
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
        score_surf = title_font.render(
            f'$ {format_big_number(score)}', False, (255, 255, 255))
        score_rect = score_surf.get_rect(center=(400, 300))
        screen.blit(score_surf, score_rect)

        # Progress bar
        progress_bar = pygame.Surface((300, 45))
        progress_bar.fill((255, 255, 255))
        screen.blit(progress_bar, (50, 50))
        goal_percent = min(1, score / goals_values[goal_value_index])
        if goal_percent == 1:
            goal_value_index += 1
        progress = pygame.Surface((290 * goal_percent, 35))
        progress.fill((0, 0, 0))
        screen.blit(progress, (55, 55))

        if game_phase >= 2:
            phase_2_border = pygame.Surface((10, 350))
            phase_2_border.fill((255, 255, 255))
            screen.blit(phase_2_border, (800, 0))

            # Handle Tic-Tac-Toe logic
            for i in range(len(ttt_buttons)):
                tile = ttt_buttons[i]
                # Loop through the tiles and check for clicks
                if not board.game_over() and tile.was_clicked(screen):
                    board.move_human(i)
                    if not board.game_over():
                        board.move_ai_naive()
            # Draw tiles to the screen
            for i in range(len(ttt_buttons)):
                tile = ttt_buttons[i]
                if board.state[i] == 1 and not tile.locked:
                    tile.place_human()
                if board.state[i] == 2 and not tile.locked:
                    tile.place_ai()
                if board.state[i] == 0 and tile.locked:
                    tile.clear()
                tile.draw(screen)
            for bar in ttt_bars:
                bar.draw(screen)

            win_surf = body_font.render(
                f'Wins: {format_big_number(wins)}', False, (255, 255, 255))
            win_rect = win_surf.get_rect(center=(400, 250))
            screen.blit(win_surf, win_rect)

            if wins >= 5 and upgrade_ttt_timer.locked:
                unlocks[3] = False
            if wins >= 10 and upgrade_ttt_power.locked:
                unlocks[4] = False
            upgrade_ttt_timer.locked = unlocks[3]
            upgrade_ttt_power.locked = unlocks[4]

            if upgrade_ttt_timer.draw(screen):
                price = get_linear_price(upgrade_ttt_timer.id)
                if price <= wins:
                    wins -= price
                    ttt_cooldown -= 1
                    upgrades[3] += 1
            if upgrade_ttt_power.draw(screen):
                price = get_linear_price(upgrade_ttt_power.id)
                if price <= wins:
                    wins -= price
                    money_per_win += 1
                    upgrades[4] += 1

        if game_phase >= 3:
            phase_3_border = pygame.Surface((1450, 10))
            phase_3_border.fill((255, 255, 255))
            screen.blit(phase_3_border, (0, 345))

            if not quiz.answer:
                quiz.generate_problem()
            math_problem_surf = giant_font.render(
                quiz.problem, False, (255, 255, 255))
            math_problem_rect = math_problem_surf.get_rect(center=(500, 475))
            screen.blit(math_problem_surf, math_problem_rect)

            if option_1.draw(screen):
                if quiz.options[0] == quiz.answer:
                    iq += 1
                else:
                    iq = max(iq - 1, 0)
                quiz.generate_problem()
            option_1_text = math_font.render(
                str(quiz.options[0]), False, (255, 255, 255))
            option_1_text_rect = option_1_text.get_rect(center=(180, 640))
            screen.blit(option_1_text, option_1_text_rect)
            if option_2.draw(screen):
                if quiz.options[1] == quiz.answer:
                    iq += 1
                else:
                    iq = max(iq - 1, 0)
                quiz.generate_problem()
            option_2_text = math_font.render(
                str(quiz.options[1]), False, (255, 255, 255))
            option_2_text_rect = option_2_text.get_rect(center=(480, 640))
            screen.blit(option_2_text, option_2_text_rect)
            if option_3.draw(screen):
                if quiz.options[2] == quiz.answer:
                    iq += 1
                else:
                    iq = max(iq - 1, 0)
                quiz.generate_problem()
            option_3_text = math_font.render(
                str(quiz.options[2]), False, (255, 255, 255))
            option_3_text_rect = option_3_text.get_rect(center=(780, 640))
            screen.blit(option_3_text, option_3_text_rect)

            iq_surf = body_font.render(
                f'IQ: {format_big_number(iq)}', False, (255, 255, 255))
            iq_rect = iq_surf.get_rect(center=(400, 215))
            screen.blit(iq_surf, iq_rect)

            if upgrade_math_power.draw(screen):
                price = get_quadratic_price(upgrade_math_power.id)
                if price <= iq:
                    iq -= price
                    wins_per_game += 1
                    upgrades[5] += 1
            if upgrade_score_multiplier.draw(screen):
                price = get_quadratic_price(upgrade_score_multiplier.id)
                if price <= iq:
                    iq -= price
                    score_multiplier += 1
                    upgrades[6] += 1

        if game_phase >= 4:
            phase_4_border = pygame.Surface((10, 800))
            phase_4_border.fill((255, 255, 255))
            screen.blit(phase_4_border, (1445, 0))
            screen.blit(trophy_surf, (trophy_rect.x, trophy_rect.y))

            if iq >= 10 and upgrade_math_power.locked:
                unlocks[5] = False
            upgrade_math_power.locked = unlocks[5]

        pygame.display.update()
        clock.tick(60)

        if board.game_over():
            if not cooldown:
                cooldown = max(1000 * ttt_cooldown, 500)
                start = pygame.time.get_ticks()
                if board.check_winner(1):
                    score += 1000 * money_per_win
                    wins += wins_per_game
            now = pygame.time.get_ticks()
            if now - start > cooldown:
                board = GameBoard()
                cooldown = None
except KeyboardInterrupt:
    print('\nquitting...')
# ----------------------------------------------------------------------------------------------------------------------
pygame.quit()
data['score'] = score
data['upgrades'] = upgrades
data['upgrade_unlocks'] = unlocks
data['game_phase'] = game_phase
data['wins'] = wins
data['iq'] = iq

with open(filename, 'w') as file:
    json.dump(data, file)
