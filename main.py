from pygame.sprite import Sprite
import pygame as pg
from sys import exit
from shared_functs import load_image, MouseLocationSprite as MSloc
from random import choice

# All static stuff
FPS = 60
WINDOW_SIZE = (800, 800)
DIFFICULTY_LIST = ['easy', 'normal', 'hard']


# Buttons events (for all menus)
def create_pair_ev(key='default'):
    return pg.event.Event(pg.USEREVENT, key=key + 'F'), pg.event.Event(pg.USEREVENT, key=key + 'UF')


StartBtnEv = create_pair_ev('ST')
SettingsBtnEv = create_pair_ev('SE')
SaveBtnEv = create_pair_ev('SV')
BackMenuBtnEv = create_pair_ev('BM')
RightArrowBtnEv = create_pair_ev('RA')
LeftArrowBtnEv = create_pair_ev('LA')
RestartGameBtnEv = create_pair_ev('RG')
RestartStatsBtnEv = create_pair_ev('RS')

# Game events
LazerStrikeAttack = pg.event.Event(pg.USEREVENT, key='LazersStrike')
GameDefeat = pg.event.Event(pg.USEREVENT, key='GD')


class Button(Sprite):
    def __init__(self, group, pos_x, pos_y, clicked_pic, unclicked_pic, event, folder):
        super().__init__(group)
        self.folder = folder
        self.image = load_image(unclicked_pic, folder=self.folder)
        self.rect = self.image.get_rect()
        self.rect.x = WINDOW_SIZE[0] * pos_x - self.rect.w * 0.5
        self.rect.y = WINDOW_SIZE[1] * pos_y
        self.clicked_pic = clicked_pic
        self.unclicked_pic = unclicked_pic
        self.event = event

    def update(self, *args, **kwargs) -> None:
        '''Checks if user's cursor overlaps the button'''
        if pg.sprite.collide_rect(self, MSloc(pg.mouse.get_pos())):
            self.image = load_image(self.clicked_pic, folder=self.folder)
            pg.event.post(self.event[0])
        else:
            self.image = load_image(self.unclicked_pic, folder=self.folder)
            pg.event.post(self.event[1])


class Picture(Sprite):
    def __init__(self, group, pos_x, pos_y, picture, folder):
        super().__init__(group)
        self.folder = folder
        self.image = load_image(picture, folder=folder)
        self.rect = self.image.get_rect()
        self.rect.x = WINDOW_SIZE[0] * pos_x - self.rect.w * 0.5
        self.rect.y = WINDOW_SIZE[1] * pos_y


class MainMenu:
    def __init__(self):
        self.buttons = pg.sprite.Group()
        self.st_btn = Button(self.buttons, 0.5, 0.2, 'start_clicked.png',
                             'start_unclicked.png', StartBtnEv, folder=r'data\menu')
        self.set_btn = Button(self.buttons, 0.5, 0.4, 'settings_clicked.png',
                              'settings_unclicked.png', SettingsBtnEv, folder=r'data\menu')

    def update(self):
        self.buttons.update()

    def draw(self, surface):
        self.buttons.draw(surface)


class Settings:
    def __init__(self):
        self.buttons = pg.sprite.Group()
        self.pictures = pg.sprite.Group()
        self.save_btn = Button(self.buttons, 0.8, 0.75, 'save_clicked.png',
                               'save_unclicked.png', SaveBtnEv, folder=r'data\settings')
        self.return_btn = Button(self.buttons, 0.2, 0.75, 'return_clicked.png',
                                 'return_unclicked.png', BackMenuBtnEv, folder=r'data\settings')

        self.right_arrow = Button(self.buttons, 0.61, 0.45, 'arrow_right_clicked.png',
                                  'arrow_right_unclicked.png', RightArrowBtnEv, folder=r'data\settings')
        self.left_arrow = Button(self.buttons, 0.39, 0.45, 'arrow_left_clicked.png',
                                 'arrow_left_unclicked.png', LeftArrowBtnEv, folder=r'data\settings')

        class Difficulty(Picture):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def switch_difficulty(self, difficulty_name):
                self.image = load_image(difficulty_name, folder=self.folder)

        with open('data/settings.txt', 'r') as f:
            diffifulty = f.read()
            if diffifulty not in DIFFICULTY_LIST:
                diffifulty = 'easy.png'
            else:
                diffifulty = diffifulty + '.png'
        self.difficulty_pic = Difficulty(self.pictures, 0.5, 0.45, diffifulty, r'data\settings\difficulty')

    def update(self):
        self.pictures.update()
        self.buttons.update()

    def draw(self, surface):
        self.pictures.draw(surface)
        self.buttons.draw(surface)


class EndScreen:
    def __init__(self):
        self.buttons = pg.sprite.Group()
        self.font = pg.font.SysFont('sen-serif', 72)
        self.update_score()
        self.return_btn = Button(self.buttons, 0.2, 0.8, 'return_clicked.png',
                                 'return_unclicked.png', BackMenuBtnEv, folder=r'data\endscreen')
        self.restartgame_btn = Button(self.buttons, 0.8, 0.8, 'restart_clicked.png',
                                      'restart_unclicked.png', RestartGameBtnEv, folder=r'data\endscreen')
        self.restartstart_btn = Button(self.buttons, 0.5, 0.55, 'res_stat_clicked.png',
                                       'res_stat_unclicked.png', RestartStatsBtnEv, folder=r'data\endscreen')

    def show_score(self, y, message, score):
        score = self.font.render(f'{message}: {score}', True, (0, 180, 0))
        size = score.get_size()
        screen.blit(score, (WINDOW_SIZE[0] * 0.5 - size[0] * 0.5, y))

    def update_score(self):
        self.top_score = open(r'data\topscore.txt').read()
        self.cur_score = open(r'data\currentscore.txt').read()

    def draw(self, surface):
        self.show_score(100, 'Top score', self.top_score)
        self.show_score(200, 'Current Score', self.cur_score)
        self.buttons.draw(surface)

    def update(self):
        self.buttons.update()


class BorderBlock(Sprite):
    def __init__(self, group, pos_x, pos_y, pic='wall.png'):
        super(BorderBlock, self).__init__(group)
        self.image = load_image(pic, folder='data\game')
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y


class LazerPlace(BorderBlock):
    def __init__(self, group, pos_x, pos_y, orientation=0, pic='lazerPlace.png'):
        super(LazerPlace, self).__init__(group, pos_x, pos_y, pic)
        if orientation == 1:
            self.image = pg.transform.rotate(self.image, 90)
            self.rect = self.image.get_rect()
            self.rect.x = pos_x
            self.rect.y = pos_y


class BorderLazer(Sprite):
    def __init__(self, group, pos_x, pos_y, orientation=0, pic='border_lazer.png'):
        super(BorderLazer, self).__init__(group)
        if orientation == 0:
            self.image = load_image(pic, folder='data\game')
        elif orientation == 1:
            self.image = pg.transform.rotate(load_image(pic, folder='data\game'), 90)
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y


class AttackingLazer(BorderLazer):
    def __init__(self, group, pos_x, pos_y, orientation, pic='attacking_lazer.png'):
        super(AttackingLazer, self).__init__(group, pos_x, pos_y, orientation, pic)


class Player(Sprite):
    def __init__(self, group):
        super(Player, self).__init__(group)
        self.image = load_image('player.png', folder='data\game')
        self.rect = self.image.get_rect()
        self.rect.x = 400
        self.rect.y = 400
        self.vel = 5
        self.last_direction = list()

    def move(self, direction, direction2):
        self.last_direction = [direction, direction2]
        self.rect = self.rect.move(direction * self.vel, direction2 * self.vel)

    def update(self, lazers, walls):
        for lazer in lazers:
            if pg.sprite.collide_mask(self, lazer):
                self.restart()
                pg.event.post(GameDefeat)

        for wall in walls:
            if pg.sprite.collide_mask(self, wall):
                self.rect.move(-self.last_direction[0] * self.vel, -self.last_direction[1] * self.vel)

    def restart(self):
        self.rect.x = 400
        self.rect.y = 400


class ScoreBoard(object):
    def __init__(self):
        self.default_pos = (WINDOW_SIZE[0] * 0.5, 30)
        self.font = pg.font.SysFont('sen-serif', 36)
        self.score = 0

    def show_score(self):
        score = self.font.render(f'Current Score: {self.score}', True, (0, 180, 0))
        size = score.get_size()
        screen.blit(score, (self.default_pos[0] - size[0] * 0.5, 30))

    def update_score(self, point):
        self.score += point


class Reward(Sprite):
    def __init__(self, group):
        super(Reward, self).__init__(group)
        self.spawn_field = [(193, 387), (217, 608)]
        self.image = load_image('coin.png', folder='data\game')
        self.rect = self.image.get_rect()
        self.point = 0

    def spawn_reward(self):
        self.image = load_image('coin.png', folder='data\game')
        self.rect = self.image.get_rect()
        self.rect.x = choice(range(*self.spawn_field[0]))
        self.rect.y = choice(range(*self.spawn_field[1]))

    def update(self, player):
        if pg.sprite.collide_mask(self, player):
            self.point = 1
        else:
            self.point = 0

    def get_point(self):
        return self.point


class Attacks(object):
    def __init__(self):
        """0 goes for 2 lazers' attack, 1 goes for 4 lazers', 2 goes for 18 lazer attack"""
        self.attack_types = list()
        self.chosen_lazers = list()

    def initilialize_lazers(self, group):
        for x in self.chosen_lazers:
            (AttackingLazer(group, 90, 192 + x[0] * 42, orientation=0,
                            pic='attack_lazer_prep.png'),
             AttackingLazer(group, 172 + x[1] * 42, 110, orientation=1,
                            pic='attack_lazer_prep.png'))

    def start_attack_phase(self, group):
        for x in self.chosen_lazers:
            (AttackingLazer(group, 90, 192 + x[0] * 42, orientation=0,
                            pic='attack_lazer_strike.png'),
             AttackingLazer(group, 172 + x[1] * 42, 110, orientation=1,
                            pic='attack_lazer_strike.png'))

    def get_to_numbers(self, iter):
        choice_list = list(range(10))
        numbers = []
        for z in range(iter):
            chosen = choice(choice_list)
            choice_list.remove(chosen)
            numbers.append(chosen)
        return numbers

    def choose_attack_and_start_prep_phase(self, group):
        self.chosen_lazers = list()
        attack = choice(self.attack_types)
        if attack == 0:
            self.chosen_lazers = [(choice(range(10)), choice(range(10)))]
        elif attack == 1:
            for x, y in zip(self.get_to_numbers(2), self.get_to_numbers(2)):
                self.chosen_lazers.append((x, y))
        else:
            l_num = choice([3, 4])
            for x, y in zip(self.get_to_numbers(l_num), self.get_to_numbers(l_num)):
                self.chosen_lazers.append((x, y))
        self.initilialize_lazers(group)

    def update_attacks(self, difficulty):
        if difficulty == 'easy':
            self.attack_types = [0]
        elif difficulty == 'normal':
            self.attack_types = [0, 1]
        elif difficulty == 'hard':
            self.attack_types = [0, 1, 2]


class Game:
    def __init__(self):
        # Gamefield
        self.lazer_places = pg.sprite.Group()
        self.borders = pg.sprite.Group()
        self.border_lazers = pg.sprite.Group()
        self.attacking_lazers = pg.sprite.Group()
        self.stat_sprites = pg.sprite.Group()
        self.lazers = pg.sprite.Group()
        border_lazers_horizontal = (
            BorderLazer(self.border_lazers, 170, 150, orientation=0),
            BorderLazer(self.border_lazers, 170, 630, orientation=0))
        border_lazers_vertical = (
            BorderLazer(self.border_lazers, 130, 190, orientation=1),
            BorderLazer(self.border_lazers, 610, 190, orientation=1))
        borders = (BorderBlock(self.borders, 110, 130), BorderBlock(self.borders, 610, 130),
                   BorderBlock(self.borders, 110, 630), BorderBlock(self.borders, 610, 630))
        lazer_place = (
            LazerPlace(self.lazer_places, 170, 80, orientation=1),
            LazerPlace(self.lazer_places, 170, 710, orientation=1),
            LazerPlace(self.lazer_places, 60, 190), LazerPlace(self.lazer_places, 690, 190))
        for x in (self.lazer_places.sprites() + self.borders.sprites() + self.border_lazers.sprites()):
            self.stat_sprites.add(x)

        # Player
        self.playerG = pg.sprite.Group()
        self.player = Player(self.playerG)

        # ScoreBoard
        self.scoreBoard = ScoreBoard()

        # Reward
        self.rewardG = pg.sprite.Group()
        self.reward = Reward(self.rewardG)
        self.reward_status = False

    def spawn_reward(self):
        self.reward.spawn_reward()
        self.reward_status = True

    def update(self, lazers):
        self.stat_sprites.update()
        self.playerG.update(lazers, self.borders)
        self.attacking_lazers.update()
        self.reward.update(self.player)
        st = self.reward.get_point()
        # Checking if reward is taken
        if st:
            self.spawn_reward()
        self.scoreBoard.update_score(st)
        self.scoreBoard.show_score()

    def draw(self, surface):
        self.stat_sprites.draw(surface)
        self.playerG.draw(surface)
        if self.reward.image:
            self.rewardG.draw(surface)
        self.attacking_lazers.draw(surface)

    def clear(self):
        self.scoreBoard.score = 0
        self.reward_status = False
        self.player.restart()


class Mode:
    def switch_to_mainMenu(self):
        running = True
        start = False
        settings = False
        menuClock = pg.time.Clock()
        while running:
            ev_list = pg.event.get()
            for ev in ev_list:
                if ev.type == pg.QUIT:
                    exit()
                if ev.type == pg.USEREVENT:
                    if ev.key == 'STF':
                        start = True
                    elif ev.key == 'STUF':
                        start = False
                    elif ev.key == 'SEF':
                        settings = True
                    elif ev.key == 'SEUF':
                        settings = False

                elif ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                    if start:
                        self.post('game')
                        running = False
                    elif settings:
                        self.post('settings')
                        running = False

            screen.fill((0, 0, 0))
            menu.update()
            menu.draw(screen)
            pg.display.flip()
            menuClock.tick(FPS)

    def switch_to_game(self):
        running = True
        gameClock = pg.time.Clock()
        difficulty = open('data/settings.txt').read()
        if not game.reward_status:
            game.spawn_reward()
        attackChoice.update_attacks(difficulty)
        if difficulty == 'easy':
            difficulty_coef = 1.25
        elif difficulty == 'normal':
            difficulty_coef = 1
        else:
            difficulty_coef = 1

        timer = 0
        attack_start = None
        attack_in_progress = None
        attacking_lazers = pg.sprite.Group()

        while running:
            ev_list = pg.event.get()
            for ev in ev_list:
                if ev.type == pg.QUIT:
                    exit()
                if ev.type == pg.USEREVENT:
                    if ev.key == 'GD':
                        running = False
            if not timer % 40 * difficulty_coef and timer > 20 * difficulty_coef and not \
                    (attack_start or attack_in_progress):
                attack_start = int(timer)
                attackChoice.choose_attack_and_start_prep_phase(attacking_lazers)

            if attack_start:
                if timer - attack_start == 100 * difficulty_coef:
                    attacking_lazers.empty()
                    attackChoice.start_attack_phase(attacking_lazers)
                    attack_start = None
                    attack_in_progress = int(timer)

            if attack_in_progress:
                if timer - attack_in_progress == 150:
                    attacking_lazers.empty()
                    attack_in_progress = None

            keys = pg.key.get_pressed()

            if keys[pg.K_a]:
                direction1 = -1
            elif keys[pg.K_d]:
                direction1 = 1
            else:
                direction1 = 0

            if keys[pg.K_w]:
                direction2 = -1
            elif keys[pg.K_s]:
                direction2 = 1
            else:
                direction2 = 0

            screen.fill((0, 0, 0))
            game.update(attacking_lazers.sprites() + game.border_lazers.sprites())
            game.player.move(direction1, direction2)
            game.draw(surface=screen)
            attacking_lazers.draw(surface=screen)
            pg.display.flip()
            timer += 1
            timer %= 1000000
            gameClock.tick_busy_loop(FPS)

        with open('data/currentscore.txt', 'w') as f:
            f.write(str(game.scoreBoard.score))
        with open('data/topscore.txt', 'r') as f:
            top_score = max(int(f.read()), game.scoreBoard.score)
        with open('data/topscore.txt', 'w') as f:
            f.write(str(top_score))

        game.clear()
        self.post('endscreen')

    def switch_to_settings(self):
        with open('data/settings.txt', 'r') as f:
            difficulty = f.read()
            if difficulty == 'easy':
                difficulty_ind = 0
            elif difficulty == 'normal':
                difficulty_ind = 1
            elif difficulty == 'hard':
                difficulty_ind = 2
            else:
                difficulty_ind = 0

        running = True
        save = False
        returnMenu = False
        r_a = False
        l_a = False
        settingsClock = pg.time.Clock()
        while running:
            ev_list = pg.event.get()
            for ev in ev_list:
                if ev.type == pg.QUIT:
                    exit()
                if ev.type == pg.USEREVENT:
                    if ev.key == 'SVF':
                        save = True
                    elif ev.key == 'SVUF':
                        save = False
                    elif ev.key == 'BMF':
                        returnMenu = True
                    elif ev.key == 'BMUF':
                        returnMenu = False
                    elif ev.key == 'RAF':
                        r_a = True
                    elif ev.key == 'RAUF':
                        r_a = False
                    elif ev.key == 'LAF':
                        l_a = True
                    elif ev.key == 'LAUF':
                        l_a = False

                elif ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                    if save:
                        with open('data\settings.txt', 'w') as file:
                            file.write(DIFFICULTY_LIST[difficulty_ind])
                    elif returnMenu:
                        self.post('menu')
                        running = False
                    elif r_a:
                        if difficulty_ind + 1 <= 2:
                            difficulty_ind += 1
                            settings.difficulty_pic.switch_difficulty(DIFFICULTY_LIST[difficulty_ind] + '.png')
                    elif l_a:
                        if difficulty_ind - 1 >= 0:
                            difficulty_ind -= 1
                            settings.difficulty_pic.switch_difficulty(DIFFICULTY_LIST[difficulty_ind] + '.png')

            screen.fill((0, 0, 0))
            settings.update()
            settings.draw(screen)
            pg.display.flip()
            settingsClock.tick(FPS)

    def switch_to_end_screen(self):
        endscreen.update_score()
        running = True
        restartGame = False
        restartStats = False
        returnMenu = False
        endscreenClock = pg.time.Clock()
        while running:
            events_list = pg.event.get()
            for ev in events_list:
                if ev.type == pg.QUIT:
                    exit()
                elif ev.type == pg.USEREVENT:
                    if ev.key == 'BMF':
                        returnMenu = True
                    elif ev.key == 'BMUF':
                        returnMenu = False
                    elif ev.key == 'RGF':
                        restartGame = True
                    elif ev.key == 'RGUF':
                        restartGame = False
                    elif ev.key == 'RSF':
                        restartStats = True
                    elif ev.key == 'RSUF':
                        restartStats = False
                elif ev.type == pg.MOUSEBUTTONDOWN and ev.button == 1:
                    if returnMenu:
                        running = False
                        self.post('menu')
                    elif restartGame:
                        running = False
                        self.post('game')
                    elif restartStats:
                        with open('data/topscore.txt', 'w') as f:
                            f.write('0')
                        endscreen.update_score()

            screen.fill((0, 0, 0))
            endscreen.update()
            endscreen.draw(screen)
            pg.display.flip()
            endscreenClock.tick(FPS)

    def post(self, ev):
        global modeEvList
        modeEvList.append(ev)


screen = pg.display.set_mode(WINDOW_SIZE)
pg.display.set_caption('MYCOIN')

# Basic settings
pg.init()
running = True
modeEvList = ['menu']

# Event timers

menu = MainMenu()
settings = Settings()
game = Game()
mode = Mode()
attackChoice = Attacks()
endscreen = EndScreen()

while running:
    if modeEvList:
        ev = modeEvList.pop(0)
        if ev == 'menu':
            mode.switch_to_mainMenu()
        elif ev == 'settings':
            mode.switch_to_settings()
        elif ev == 'game':
            mode.switch_to_game()
        elif ev == 'endscreen':
            mode.switch_to_end_screen()
