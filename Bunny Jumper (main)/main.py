import pygame as pg
from os import path
import random
from settings import *
from sprites import *


class Game:
    def __init__(self):
        # инициализирует окно игры, и т. д.
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font_name = pg.font.match_font(NAME_FONT)
        self.load_data()
        self.exit_game = False
        self.restat = False
        self.pause = False
        self.not_gov = True

    def load_data(self):
        # загруска high score
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, HS_FILE), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        # загружает картинки с spritsheet
        img_dir = path.join(self.dir, 'images')
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        # сохраняет облака картинки
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(
                pg.image.load(path.join(
                    img_dir, 'cloud{}.png'.format(i))).convert())
        # загружает звуки
        self.snd_dir = path.join(self.dir, 'sounds')
        self.jump_sound = pg.mixer.Sound(
            path.join(self.snd_dir, 'Jump33.wav'))
        self.boost_sound = pg.mixer.Sound(
            path.join(self.snd_dir, 'Carrot.wav'))

    def new(self):
        # запускает новую игру
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.player = Player(self)
        for plat in PLATFORM_LIST:
            Platform(self, *plat)
        self.mob_timer = 0
        pg.mixer.music.load(path.join(self.snd_dir, 'game_music.mp3'))
        for i in range(8):
            c = Cloud(self)
            c.rect.y += 500
        self.run()

    def run(self):
        # Запускает все процессы
        pygame.display.set_icon(ICON_SURF)
        pg.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    if self.playing:
                        self.playing = False
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    evp = event.pos
                    if (467 >= evp[0] >= 430) & (39 >= evp[1] >= 0):
                        if self.playing:
                            self.playing = False
                        self.exit_game = True
                    elif (466 >= evp[0] >= 428) & (87 >= evp[1] >= 47):
                        self.pause = True
                        while self.pause:
                            self.screen.blit(CONTINUE_GAME, (0, 0))
                            pg.display.update()
                            for event in pg.event.get():
                                if event.type == pg.QUIT:
                                    if self.playing:
                                        self.playing = False
                                    self.running = False
                                    self.pause = False
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    evp = event.pos
                                    if (467 >= evp[0] >= 430) & \
                                       (39 >= evp[1] >= 0):
                                        if self.playing:
                                            self.playing = False
                                        self.pause = False
                                        self.exit_game = True
                                    elif (466 >= evp[0] >= 428) & \
                                         (87 >= evp[1] >= 47):
                                        self.pause = False
                                    elif (468 >= evp[0] >= 429) & \
                                         (130 >= evp[1] >= 93):
                                        if self.playing:
                                            self.playing = False
                                        self.pause = False
                                        self.restat = True
                    elif (468 >= evp[0] >= 429) & (130 >= evp[1] >= 93):
                        if self.playing:
                            self.playing = False
                        self.restat = True
            self.player.jump()
            self.clock.tick(FPS)
            self.render()
            self.draw()
        pg.mixer.music.fadeout(500)

    def render(self):
        pygame.display.set_icon(ICON_SURF)
        self.all_sprites.update()
        self.player.jump()

        # спавн монстров
        now = pg.time.get_ticks()
        if self.score >= 150:
            if now - self.mob_timer > 5000 + \
                            random.choice([-1000, -500, 0, 500, 1000]):
                self.mob_timer = now
                Mob(self)
        # если монстра задеть
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False)
        if mob_hits:
            self.playing = False

        # проверка, попадает ли игрок на платформу - только если падает
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 15 and \
                   self.player.pos.x > lowest.rect.left - 15:
                    if self.player.pos.y < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top
                        self.player.vel.y = 0
                        self.player.jumping = False

        # если игрок достигает верхней 1/4 экрана
        if self.player.rect.top <= HEIGHT / 4:
            if random.randrange(100) < 15:
                Cloud(self)
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y / 2), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10

        # если игрок соберает буст (монетку)
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -BOOST
                self.player.jumping = False

        # если игрок умирает
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        # порождает новые платформы
        while len(self.platforms) < 6:
            width = random.randrange(50, 110)
            Platform(self, random.randrange(0, WIDTH - width),
                     random.randrange(-75, -30))

    def draw(self):
        # В игре зацикленна функция
        self.screen.fill(BGCOLORINGAME)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 25, BLACK, WIDTH / 2, 15)
        # Рисует задний цвет фона, все справайты и счётчик
        self.screen.blit(LITLE_LEFTUP_MENU, (0, 0))
        pg.display.flip()

    def show_start_screen(self):
        # начальная сцена игры/старт игры
        pygame.display.set_icon(ICON_SURF)
        pg.mixer.music.load(path.join(self.snd_dir, 'menu_music.mp3'))
        pg.mixer.music.play(loops=-1)
        self.screen.blit(BGCOLOR, (0, 0))
        self.draw_text(TITLE, 48, BLACK, WIDTH / 2 + 1.9, HEIGHT / 4 + 1.9)
        self.draw_text(
            "Arrows to move, Jump automatically", 22,
            BLACK, WIDTH / 2 + 1.9, HEIGHT / 2 + 1.9)
        self.draw_text(
            "Press any key to play", 22,
            BLACK, WIDTH / 2 + 1.9, HEIGHT * 3 / 4 + 1.9)
        self.draw_text(
            "High Score: " + str(self.highscore), 22,
            BLACK, WIDTH / 2 + 1.9, 16.9)
        self.draw_text(TITLE, 48, ORANGE, WIDTH / 2, HEIGHT / 4)
        self.draw_text(
            "Arrows to move, Jump automatically", 22,
            ORANGE, WIDTH / 2, HEIGHT / 2)
        self.draw_text(
            "Press any key to play", 22, ORANGE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text(
            "High Score: " + str(self.highscore), 22, ORANGE, WIDTH / 2, 15)
        self.screen.blit(PREV_NEXT_EXIT, (0, 0))
        pg.display.flip()
        self.wait_for_key_in_main()
        pg.mixer.music.fadeout(500)

    def show_game_screen(self):
        # игра окончена/продолжить
        pygame.display.set_icon(ICON_SURF)
        if self.restat or self.exit_game:
            pg.display.update()
            self.wait_for_key_in_main()
        else:
            if not self.running:
                return
            pg.mixer.music.load(path.join(self.snd_dir, 'menu_music.mp3'))
            pg.mixer.music.play(loops=-1)
            self.screen.blit(BGCOLOR_FAIL, (0, 0))
            self.draw_text(
                "GAME OVER", 48, BLACK, WIDTH / 2 + 1.9, HEIGHT / 4 + 1.9)
            self.draw_text("Score: " + str(self.score),
                           22, BLACK, WIDTH / 2 + 1.9, HEIGHT / 2 + 1.9)
            self.draw_text("Press  any  key  to  play  again",
                           22, BLACK, WIDTH / 2 + 1.9, HEIGHT * 3 / 4 + 1.9)
            if self.score > self.highscore:
                self.highscore = self.score
                self.draw_text("NEW HIGH SCORE!",
                               22, BLACK, WIDTH / 2 + 1.9, HEIGHT / 2 + 41.9)
                self.highscore = self.score
                self.draw_text("NEW HIGH SCORE!",
                               22, ORANGE, WIDTH / 2, HEIGHT / 2 + 40)
                with open(path.join(self.dir, HS_FILE), 'w') as f:
                    f.write(str(self.score))
            else:
                self.draw_text("High Score: " + str(self.highscore),
                               22, BLACK, WIDTH / 2 + 1.9, HEIGHT / 2 + 41.9)
                self.draw_text("High Score: " + str(self.highscore),
                               22, ORANGE, WIDTH / 2, HEIGHT / 2 + 40)
            self.draw_text("GAME OVER", 48, ORANGE, WIDTH / 2, HEIGHT / 4)
            self.draw_text("Score: " + str(self.score),
                           22, ORANGE, WIDTH / 2, HEIGHT / 2)
            self.draw_text("Press  any  key  to  play  again",
                           22, ORANGE, WIDTH / 2, HEIGHT * 3 / 4)
            self.not_gov = False
            self.screen.blit(EXITBUTTON, (0, 0))
            pg.display.update()
            self.wait_for_key_in_main()
            pg.mixer.music.fadeout(500)

    def wait_for_key_in_main(self):
        # Ожидает пока пользователь не нажмёт на любую кнопку
        pygame.display.set_icon(ICON_SURF)
        expectation = True
        while expectation:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    expectation = False
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    evp = event.pos
                    if (119 >= evp[0] >= 64) & \
                       (595 >= evp[1] >= 542) & self.not_gov:
                        game_2 = next_Game_2()
                        game_2.show_start_screen()
                        while game_2.running:
                            game_2.new()
                            game_2.show_game_screen()
                        expectation = False
                        self.running = False
                    elif (470 >= evp[0] >= 410) & (600 >= evp[1] >= 540):
                        expectation = False
                        self.running = False
                if event.type == pg.KEYDOWN:
                    expectation = False
            if self.exit_game:
                expectation = False
                self.exit_game = False
                self.show_start_screen()
            elif self.restat:
                expectation = False
                self.restat = False
        self.not_gov = True

    def draw_text(self, text, size, color, x, y):
        # Работа с текстом
        pygame.display.set_icon(ICON_SURF)
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


class next_Game_2(Game):
    def __init__(self):
        Game.__init__(self)

    def load_data(self):
        # загруска high score
        pygame.display.set_icon(ICON_SURF)
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, HS_FILE_2), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        # загружает картинки с spritsheet
        img_dir = path.join(self.dir, 'images')
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        # сохраняет облака картинки
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(
                pg.image.load(path.join(
                    img_dir, 'cloud{}.png'.format(i))).convert())
        # загружает звуки
        self.snd_dir = path.join(self.dir, 'sounds')
        self.jump_sound = pg.mixer.Sound(
            path.join(self.snd_dir, 'Jump33.wav'))
        self.boost_sound = pg.mixer.Sound(
            path.join(self.snd_dir, 'Carrot.wav'))

    def show_start_screen(self):
        # начальная сцена игры/старт игры
        pygame.display.set_icon(ICON_SURF)
        pg.mixer.music.load(path.join(self.snd_dir, 'menu_music_2.mp3'))
        pg.mixer.music.play(loops=-1)
        self.screen.blit(BGCOLOR_2, (0, 0))
        self.draw_text(TITLE, 48, BLACK, WIDTH / 2 + 1.9, HEIGHT / 4 + 1.9)
        self.draw_text(
            "Arrows to move, Jump automatically", 22,
            BLACK, WIDTH / 2 + 1.9, HEIGHT / 2 + 1.9)
        self.draw_text(
            "Press any key to play", 22,
            BLACK, WIDTH / 2 + 1.9, HEIGHT * 3 / 4 + 1.9)
        self.draw_text(
            "High Score: " + str(
                self.highscore), 22, BLACK, WIDTH / 2 + 1.9, 16.9)
        self.draw_text(TITLE, 48, PURPLE, WIDTH / 2, HEIGHT / 4)
        self.draw_text(
            "Arrows to move, Jump automatically", 22,
            PURPLE, WIDTH / 2, HEIGHT / 2)
        self.draw_text(
            "Press any key to play", 22, PURPLE, WIDTH / 2, HEIGHT * 3 / 4)
        self.draw_text(
            "High Score: " + str(self.highscore), 22, PURPLE, WIDTH / 2, 15)
        self.screen.blit(PREV_NEXT_EXIT_2, (0, 0))
        pg.display.flip()
        self.wait_for_key_in_main()
        pg.mixer.music.fadeout(500)

    def show_game_screen(self):
        # игра окончена/продолжить
        pygame.display.set_icon(ICON_SURF)
        if self.restat or self.exit_game:
            pg.display.update()
            self.wait_for_key_in_main()
        else:
            if not self.running:
                return
            pg.mixer.music.load(path.join(self.snd_dir, 'menu_music_2.mp3'))
            pg.mixer.music.play(loops=-1)
            self.screen.blit(BGCOLOR_FAIL_2, (0, 0))
            self.draw_text(
                "GAME OVER", 48, BLACK, WIDTH / 2 + 1.9, HEIGHT / 4 + 1.9)
            self.draw_text("Score: " + str(self.score),
                           22, BLACK, WIDTH / 2 + 1.9, HEIGHT / 2 + 1.9)
            self.draw_text("Press  any  key  to  play  again",
                           22, BLACK, WIDTH / 2 + 1.9, HEIGHT * 3 / 4 + 1.9)
            if self.score > self.highscore:
                self.highscore = self.score
                self.draw_text("NEW HIGH SCORE!",
                               22, BLACK, WIDTH / 2 + 1.9, HEIGHT / 2 + 41.9)
                self.highscore = self.score
                self.draw_text("NEW HIGH SCORE!",
                               22, PURPLE, WIDTH / 2, HEIGHT / 2 + 40)
                with open(path.join(self.dir, HS_FILE_2), 'w') as f:
                    f.write(str(self.score))
            else:
                self.draw_text("High Score: " + str(self.highscore),
                               22, BLACK, WIDTH / 2 + 1.9, HEIGHT / 2 + 41.9)
                self.draw_text("High Score: " + str(self.highscore),
                               22, PURPLE, WIDTH / 2, HEIGHT / 2 + 40)
            self.draw_text("GAME OVER", 48, PURPLE, WIDTH / 2, HEIGHT / 4)
            self.draw_text("Score: " + str(self.score),
                           22, PURPLE, WIDTH / 2, HEIGHT / 2)
            self.draw_text("Press  any  key  to  play  again",
                           22, PURPLE, WIDTH / 2, HEIGHT * 3 / 4)
            self.not_gov = False
            self.screen.blit(EXITBUTTON, (0, 0))
            pg.display.update()
            self.wait_for_key_in_main()
            pg.mixer.music.fadeout(500)

    def wait_for_key_in_main(self):
        # Ожидает пока пользователь не нажмёт на любую кнопку
        pygame.display.set_icon(ICON_SURF)
        expectation = True
        while expectation:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    expectation = False
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    evp = event.pos
                    if (55 >= evp[0] >= 0) & \
                       (595 >= evp[1] >= 542) & self.not_gov:
                        game = Game()
                        game.show_start_screen()
                        while game.running:
                            game.new()
                            game.show_game_screen()
                        expectation = False
                        self.running = False
                    elif (470 >= evp[0] >= 410) & (600 >= evp[1] >= 540):
                        expectation = False
                        self.running = False
                if event.type == pg.KEYDOWN:
                    expectation = False
            if self.exit_game:
                expectation = False
                self.exit_game = False
                self.show_start_screen()
            elif self.restat:
                expectation = False
                self.restat = False
        self.not_gov = True

    def load_data(self):
        # загруска high score
        pygame.display.set_icon(ICON_SURF)
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, HS_FILE_2), 'r') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        # загружает картинки с spritsheet
        img_dir = path.join(self.dir, 'images')
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        # сохраняет облака картинки
        self.cloud_images = []
        for i in range(1, 4):
            self.cloud_images.append(
                pg.image.load(path.join(
                    img_dir, 'cloud{}.png'.format(i))).convert())
        # загружает звуки
        self.snd_dir = path.join(self.dir, 'sounds')
        self.jump_sound = pg.mixer.Sound(
            path.join(self.snd_dir, 'Jump33.wav'))
        self.boost_sound = pg.mixer.Sound(
            path.join(self.snd_dir, 'Carrot.wav'))

    def new(self):
        # запускает новую игру
        pygame.display.set_icon(ICON_SURF)
        self.score = 0
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.clouds = pg.sprite.Group()
        self.player = Player_2(self)
        for plat in PLATFORM_LIST:
            Platform_2(self, *plat)
        self.mob_timer = 0
        pg.mixer.music.load(path.join(self.snd_dir, 'game_music_2.mp3'))
        for i in range(8):
            c = Cloud(self)
            c.rect.y += 500
        self.run()

    def run(self):
        # Запускает все процессы
        pygame.display.set_icon(ICON_SURF)
        pg.mixer.music.play(loops=-1)
        self.playing = True
        while self.playing:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    if self.playing:
                        self.playing = False
                    self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    evp = event.pos
                    if (467 >= evp[0] >= 430) & (39 >= evp[1] >= 0):
                        if self.playing:
                            self.playing = False
                        self.exit_game = True
                    elif (466 >= evp[0] >= 428) & (87 >= evp[1] >= 47):
                        self.pause = True
                        while self.pause:
                            self.screen.blit(CONTINUE_GAME, (0, 0))
                            pg.display.update()
                            for event in pg.event.get():
                                if event.type == pg.QUIT:
                                    if self.playing:
                                        self.playing = False
                                    self.running = False
                                    self.pause = False
                                if event.type == pygame.MOUSEBUTTONDOWN:
                                    evp = event.pos
                                    if (467 >= evp[0] >= 430) & \
                                       (39 >= evp[1] >= 0):
                                        if self.playing:
                                            self.playing = False
                                        self.pause = False
                                        self.exit_game = True
                                    elif (466 >= evp[0] >= 428) & \
                                         (87 >= evp[1] >= 47):
                                        self.pause = False
                                    elif (468 >= evp[0] >= 429) & \
                                         (130 >= evp[1] >= 93):
                                        if self.playing:
                                            self.playing = False
                                        self.pause = False
                                        self.restat = True
                    elif (468 >= evp[0] >= 429) & (130 >= evp[1] >= 93):
                        if self.playing:
                            self.playing = False
                        self.restat = True
            self.player.jump()
            self.clock.tick(FPS)
            self.render()
            self.draw()
        pg.mixer.music.fadeout(500)

    def render(self):
        pygame.display.set_icon(ICON_SURF)
        self.all_sprites.update()
        self.player.jump()

        # спавн монстров
        now = pg.time.get_ticks()
        if now - self.mob_timer > 5000 + \
           random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob_2(self)
        # если монстра задеть
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False)
        if mob_hits:
            self.playing = False

        # проверка, попадает ли игрок на платформу - только если падает
        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player, self.platforms, False)
            if hits:
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                if self.player.pos.x < lowest.rect.right + 15 and \
                   self.player.pos.x > lowest.rect.left - 15:
                    if self.player.pos.y < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top
                        self.player.vel.y = 0
                        self.player.jumping = False

        # если игрок достигает верхней 1/4 экрана
        if self.player.rect.top <= HEIGHT / 4:
            if random.randrange(100) < 15:
                Cloud(self)
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            for cloud in self.clouds:
                cloud.rect.y += max(abs(self.player.vel.y / 2), 2)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill()
                    self.score += 10

        # если игрок соберает буст (монетку)
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = -BOOST
                self.player.jumping = False

        # если игрок умирает
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        # порождает новые платформы
        while len(self.platforms) < 5:
            width = random.randrange(50, 110)
            Platform_2(self, random.randrange(
                0, WIDTH - width), random.randrange(-75, -30))

    def draw(self):
        # В игре зацикленна функция
        pygame.display.set_icon(ICON_SURF)
        self.screen.fill(BGCOLORINGAME_2)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 25, BLACK, WIDTH / 2, 15)
        # Рисует задний цвет фона, все справайты и счётчик
        self.screen.blit(LITLE_LEFTUP_MENU, (0, 0))
        pg.display.flip()

game = Game()
game.show_start_screen()
while game.running:
    game.new()
    game.show_game_screen()
pg.quit()
