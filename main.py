import pygame
from random import randint
from Net import Neural_Net, Sheet, Bird_Sheets
import math
import json

size = width, height = 350, 500
dop_screen_w = 550

black = 0, 0, 0
g = -1
bird_start_pos = 50
porog_obj = 0
width_of_obj = 70
height_of_obj_gape = 110
vy_limit = 0.5
number_of_birds = 5
maxvy = 5

f_s = []

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode(size)
myfont = pygame.font.Font('cool_font.ttf', 40)
titlefont = pygame.font.Font('cool_font.ttf', 48)
pygame.mixer.music.load("bg.mp3")
pygame.mixer.music.play(-1)


def rud(v0, t):
    return v0 + g * t


class Bird:
    vy = 0
    x = bird_start_pos
    y = height / 2
    gameover = False
    fitnes = 0
    values = []

    def __init__(self, i):
        self.output = 0
        self.color = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.image = pygame.image.load("birds/bird" + str(i) + ".png")

    def set_values(self, vals):
        self.values = vals

    def draw(self, screen=pygame.display):
        if not self.gameover:
            surf = pygame.transform.rotate(self.image, 90 * (self.vy / maxvy))
            screen.blit(surf, (int(self.x - 15), int(self.y - 13)))

    def jump(self):
        if self.vy <= vy_limit:
            self.vy = 0.8

    def logic(self):
        self.vy = rud(self.vy, 0.005)
        self.y -= self.vy
        if self.y < 0 or self.y > height:
            return False
        return True

    def draw_info(self, screen=pygame.display, i=0):
        screen.blit(self.image, (int(width + 45), int(i * 100 + 37)))
        pygame.draw.line(screen, (200, 200, 200), (width, i * 100 + 100), (width + dop_screen_w, i * 100 + 100))

        kek = self.values[0]

        if kek < 0:
            pygame.draw.rect(screen, (0, 0, 255), (width + 100, i * 100 + 80, 10, kek // 6))
        else:
            pygame.draw.rect(screen, (255, 0, 0), (width + 100, i * 100 + 80, 10, -kek // 6))

        kek = self.values[1]

        if kek < 0:
            pygame.draw.rect(screen, (0, 0, 255), (width + 120, i * 100 + 80, 10, kek // 6))
        else:
            pygame.draw.rect(screen, (255, 0, 0), (width + 120, i * 100 + 80, 10, -kek // 6))

        kek = self.output

        pygame.draw.rect(screen, (255, 0, 0), (width + 140, i * 100 + 80, 10, -kek * 60))

        if self.gameover:
            pygame.draw.circle(screen, (255, 0, 0), (width + 60, i * 100 + 50), 20, 3)
            pygame.draw.line(screen, (255, 0, 0), (width + 75, i * 100 + 65), (width + 45, i * 100 + 35), 4)

    def draw_net(self, _net, screen=pygame.display):
        net = _net
        if self.gameover:
            self.values = [0, 0]
            net.zero()
        size_between_neurons = 100
        pygame.draw.rect(screen, (255, 255, 255), (width, 0, dop_screen_w, height))
        struct = net.layer_capacity
        xs = [0] * net.layer_count
        xs[0], xs[len(xs) - 1] = width + 50, width + dop_screen_w - 50
        gap = dop_screen_w - 100

        for i in range(1, len(xs) - 1):
            xs[i] = xs[i - 1] + gap // (len(xs) - 1)

        ys = []
        for i in range(0, net.layer_count):
            ys.append([])
            for j in range(0, struct[i]):
                ys[i].append(0)

        dy = []

        for i in range(0, len(ys)):
            if len(ys[i]) == 1:
                ys[i][0] = height // 2
            else:
                all_len = (len(ys[i]) - 1) * size_between_neurons
                k = 0
                while all_len > height - 120:
                    all_len = (len(ys[i]) - 1) * (size_between_neurons - k)
                    k += 1
                dy.append((height - all_len) // 2)
                for j in range(0, len(ys[i])):
                    ys[i][j] = dy[i] + j * (size_between_neurons - k)

        minmax = net.get_min_max()

        for i in range(0, net.layer_count - 1):
            for j in range(0, struct[i]):
                for k in range(0, struct[i + 1]):
                    val = net.axons[
                        net.get_id(i, j)
                    ][
                        net.get_id(i + 1, k)
                    ]

                    if val == 0:
                        colour = (0, 0, 0)
                    elif val > 0:
                        colour = (int(255 * (val / abs(minmax[1]))) % 255, 0, 0)
                    else:
                        colour = (0, 0, int(255 * (-val / abs(minmax[0]))) % 255)

                    pygame.draw.line(screen, colour, (xs[i], ys[i][j]), (xs[i + 1], ys[i + 1][k]), 1)

        for i in range(0, net.layer_count):
            for j in range(0, struct[i]):
                id = net.get_id(i, j)
                val = net.neurons[id].value

                if id == 0:
                    val = self.values[0]
                    if abs(val) > width:
                        if val > 0:
                            val = width
                        else:
                            val = -width
                    if val >= 0:
                        pygame.draw.circle(screen, (int(255 * (val / width)), 0, 0), (xs[i], ys[i][j]), 20)
                    else:
                        pygame.draw.circle(screen, (0, 0, int(255 * (-val / width))), (xs[i], ys[i][j]), 20)
                elif id == 1:
                    val = self.values[1]
                    if abs(val) > height:
                        if val > 0:
                            val = height
                        else:
                            val = -height
                    if val >= 0:
                        pygame.draw.circle(screen, (int(255 * (val / height)), 0, 0), (xs[i], ys[i][j]), 20)
                    else:
                        pygame.draw.circle(screen, (0, 0, int(255 * (-val / height))), (xs[i], ys[i][j]), 20)
                else:
                    if val == 0:
                        colour = (0, 0, 0)
                    elif val > 0:
                        colour = (int(255 * val), 0, 0)
                    else:
                        colour = (0, 0, int(255 * -val))
                    pygame.draw.circle(screen, colour, (xs[i], ys[i][j]), 20)


class Obstacle:
    vx = 0.0
    x = float(width)
    heigh = 0
    porog = porog_obj
    wid = width_of_obj
    gape = height_of_obj_gape
    fitness = 0

    def __init__(self):
        self.image = pygame.image.load("obstcl/1.png")
        self.heigh = randint(0 + self.porog, height - self.porog - self.gape)
        self.x = width

    def logic(self):
        self.x -= 0.5
        if self.x < -self.wid:
            return False
        return True

    def draw(self, screen):
        screen.blit(self.image, (int(self.x), self.heigh - 500))
        # pygame.draw.rect(screen, (255, 0, 255), (int(self.x), self.heigh - 500, self.wid, 500), 0)
        screen.blit(pygame.transform.rotate(self.image, 180), (int(self.x), self.heigh + height_of_obj_gape))
        # pygame.draw.rect(screen, (255, 0, 255), (int(self.x), height, self.wid, -(height - self.heigh - self.gape)), 0)

    def __eq__(self, other=Bird):
        if other.x >= self.x and other.x <= self.x + self.wid:
            if other.y < self.heigh or other.y > self.heigh + self.gape:
                return True
        return False


bg = pygame.image.load("bg.png")


def begin():
    screen = pygame.display.set_mode(size)

    gameover = False

    screen.blit(bg, (0, 0))

    title = myfont.render('NEURAL BIRD', 0, (255, 255, 255))
    solo_text = myfont.render('SOLO', 0, (255, 255, 255))
    main_text = myfont.render('ACTIVATE ML', 0, (255, 255, 255))
    multiplayer_text = myfont.render('MULTIPLAYER', 0, (255, 255, 255))
    record_title = myfont.render('RECORDS', 0, (255, 255, 255))
    screen.blit(title, (42, 40))
    screen.blit(solo_text, (42, 140))
    screen.blit(main_text, (42, 200))
    screen.blit(multiplayer_text, (42, 260))
    screen.blit(record_title, (42, 320))

    chosen = 0

    while not gameover:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    main(kill=True)
                elif event.key == pygame.K_ESCAPE:
                    gameover = True
                    quit()
                elif event.key == pygame.K_UP:
                    chosen -= 1
                    while chosen < 0:
                        chosen += 4
                elif event.key == pygame.K_DOWN:
                    chosen += 1
                    while chosen >= 4:
                        chosen -= 4
                elif event.key == pygame.K_RETURN:
                    if chosen == 0:
                        solo()
                    elif chosen == 1:
                        main()
                    elif chosen == 2:
                        multiplayer()
                    elif chosen == 3:
                        record()

        if chosen == 0:
            solo_text = myfont.render('SOLO', 0, (232, 44, 12))
            main_text = myfont.render('ACTIVATE ML', 0, (255, 255, 255))
            multiplayer_text = myfont.render('MULTIPLAYER', 0, (255, 255, 255))
            record_title = myfont.render('RECORDS', 0, (255, 255, 255))
        elif chosen == 1:
            solo_text = myfont.render('SOLO', 0, (255, 255, 255))
            main_text = myfont.render('ACTIVATE ML', 0, (232, 44, 12))
            multiplayer_text = myfont.render('MULTIPLAYER', 0, (255, 255, 255))
            record_title = myfont.render('RECORDS', 0, (255, 255, 255))
        elif chosen == 2:
            solo_text = myfont.render('SOLO', 0, (255, 255, 255))
            main_text = myfont.render('ACTIVATE ML', 0, (255, 255, 255))
            multiplayer_text = myfont.render('MULTIPLAYER', 0, (232, 44, 12))
            record_title = myfont.render('RECORDS', 0, (255, 255, 255))
        elif chosen == 3:
            solo_text = myfont.render('SOLO', 0, (255, 255, 255))
            main_text = myfont.render('ACTIVATE ML', 0, (255, 255, 255))
            multiplayer_text = myfont.render('MULTIPLAYER', 0, (232, 255, 255))
            record_title = myfont.render('RECORDS', 0, (255, 44, 12))

        screen.blit(solo_text, (42, 140))
        screen.blit(main_text, (42, 200))
        screen.blit(multiplayer_text, (42, 260))
        screen.blit(record_title, (42, 320))
        pygame.display.update()


def solo():
    screen = pygame.display.set_mode(size)
    force = False

    game_start = False
    on_pause = False

    bird = Bird(1)
    obst = Obstacle()
    gameover = False
    fitness = 0

    screen.blit(bg, (0, 0))

    bird.draw(screen)
    obst.draw(screen)

    pygame.display.update()

    while not game_start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameover = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_start = True
                elif event.key == pygame.K_ESCAPE:
                    force = True
                    game_start = True
                    gameover = True

    while not gameover:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameover = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
                elif event.key == pygame.K_p:
                    on_pause = not on_pause
                elif event.key == pygame.K_ESCAPE:
                    force = True
                    gameover = True

        if not on_pause:
            screen.blit(bg, (0, 0))

            if not obst.logic():
                obst = Obstacle()
            obst.draw(screen)
            if not bird.logic() or bird == obst:
                gameover = True
            bird.draw(screen)

            # textsurface2 = myfont.render('Input1: ' + str(-int(bird.y - (obst.heigh + 0.5*height_of_obj_gape))), False, (255, 255, 255))
            # textsurface3 = myfont.render('Input2: ' + str(int(obst.x + 0.5*width_of_obj - bird_start_pos)), False, (255, 255, 255))
            # screen.blit(textsurface1, (width - 100, 0))
            # screen.blit(textsurface2, (width - 100, 12))
            # screen.blit(textsurface3, (width - 100, 24))

            pygame.display.update()
            # pygame.time.wait(1)
            fitness += 1

    if force:
        begin()
    else:
        pygame.time.delay(1000)
        pygame.draw.rect(screen, (255, 255, 255), (45, 150, 260, 100))
        score_text = myfont.render('YOUR SCORE IS', 0, (0, 0, 0))
        f_s.append(fitness)
        score_text2 = myfont.render(str(fitness), 0, (0, 0, 0))
        screen.blit(score_text, (50, 150))
        screen.blit(score_text2, (50, 180))
        pygame.display.update()

        while game_start:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameover = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_start = False
                    elif event.key == pygame.K_ESCAPE:
                        force = True
                        gameover = True
                        game_start = False

        solo()


def record():
    f_s.sort()
    f_s.reverse()
    screen = pygame.display.set_mode(size)
    gameover = False
    while not gameover:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    gameover = True

        screen.blit(bg, (0, 0))
        title_r = myfont.render('RECORDS', 0, (255, 255, 255))
        r_1 = myfont.render('1', 0, (255, 255, 255))
        r_2 = myfont.render('2', 0, (255, 255, 255))
        r_3 = myfont.render('3', 0, (255, 255, 255))
        screen.blit(title_r, (42, 40))
        screen.blit(r_1, (42, 80))
        screen.blit(r_2, (42, 140))
        screen.blit(r_3, (42, 200))
        if len(f_s) == 1:
            record_1 = myfont.render(str(f_s[0]), 0, (0, 0, 0))
            screen.blit(record_1, (70, 80))
        elif len(f_s) == 2:
            record_1 = myfont.render(str(f_s[0]), 0, (0, 0, 0))
            record_2 = myfont.render(str(f_s[1]), 0, (0, 0, 0))
            screen.blit(record_1, (70, 80))
            screen.blit(record_2, (70, 140))
        elif len(f_s) > 2:
            record_1 = myfont.render(str(f_s[0]), 0, (0, 0, 0))
            record_2 = myfont.render(str(f_s[1]), 0, (0, 0, 0))
            record_3 = myfont.render(str(f_s[2]), 0, (0, 0, 0))
            screen.blit(record_1, (70, 80))
            screen.blit(record_2, (70, 140))
            screen.blit(record_3, (70, 200))
        pygame.display.update()
    begin()




def main(showing_mode=False, showing_bird=0, kill=False):
    screen = pygame.display.set_mode((width + dop_screen_w, height))
    force = False
    fitness = 0
    with open("nets.json") as f:
        nets = [Neural_Net(i) for i in json.load(f)["nets"]]
    with open("nets.json") as f:
        gen = json.load(f)["gen"]
    empty_net = nets[0]

    empty_net.zero()
    birds = [Bird(i + 1) for i in range(len(nets))]

    if kill:
        for i in nets:
            i.zero()
            gen = 0

    obst = Obstacle()

    gameover = False

    while not gameover:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameover = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if showing_mode:
                        showing_mode = False
                    else:
                        force = True
                        gameover = True
                        break
                elif event.key == pygame.K_1:
                    showing_mode = True
                    showing_bird = 0
                elif event.key == pygame.K_2:
                    showing_mode = True
                    showing_bird = 1
                elif event.key == pygame.K_3:
                    showing_mode = True
                    showing_bird = 2
                elif event.key == pygame.K_4:
                    showing_mode = True
                    showing_bird = 3
                elif event.key == pygame.K_5:
                    showing_mode = True
                    showing_bird = 4

        screen.blit(bg, (0, 0))
        for i in range(0, len(birds)):
            if not birds[i].gameover:
                nets[i].set_values([-int(birds[i].y - (obst.heigh + 0.5 * height_of_obj_gape)),
                                    int(obst.x + 0.5 * width_of_obj - bird_start_pos)])

                birds[i].set_values([-int(birds[i].y - (obst.heigh + 0.5 * height_of_obj_gape)),
                                     int(obst.x + 0.5 * width_of_obj - bird_start_pos)])
                nets[i].update_values()
                birds[i].output = nets[i].neurons[
                    nets[i].get_id(nets[i].layer_count - 1, nets[i].layer_capacity[nets[i].layer_count - 1] - 1)].value
                if birds[i].output >= 0.5:
                    birds[i].jump()

                if not birds[i].logic():
                    birds[i].fitnes = fitness
                    birds[i].gameover = True

                if obst == birds[i]:
                    birds[i].fitnes = fitness
                    birds[i].gameover = True

                birds[i].draw(screen)

        if not obst.logic():
            obst = Obstacle()
        obst.draw(screen)

        if not showing_mode:
            pygame.draw.rect(screen, (255, 255, 255), (width, 0, dop_screen_w, height))
            for i in range(0, len(birds)):
                birds[i].draw_info(screen, i)
        else:
            try:
                if birds[showing_bird].gameover:
                    birds[showing_bird].draw_net(empty_net, screen)
                else:
                    birds[showing_bird].draw_net(nets[showing_bird], screen)
            except Exception:
                showing_mode = False
                for i in range(0, len(birds)):
                    birds[i].draw_info(screen, i)

        score_text = myfont.render('GEN ' + str(gen), 0, (0, 0, 0))
        screen.blit(score_text, (width - 120, 10))

        pygame.display.update()
        # pygame.time.wait(1)
        fitness += 1
        all = 0
        for i in birds:
            if i.gameover:
                all += 1
        if all == number_of_birds:
            gameover = True

    for i in birds:
        if not i.gameover:
            i.fitnes = fitness

    for i in range(len(nets) - 1):
        for j in range(len(nets) - i - 1):
            if birds[j].fitnes < birds[j + 1].fitnes:
                birds[j], birds[j + 1] = birds[j + 1], birds[j]
                nets[j], nets[j + 1] = nets[j + 1], nets[j]

    # Простой механизм обучения

    nets[1] = nets[1] + nets[2]

    nets[4].random_axons()
    nets[3].random_axons()
    nets[2].random_axons()

    kek = {"gen": gen + 1, "nets": []}
    for i in nets:
        kek["nets"].append(i.save_result())

    with open("nets.json", 'w') as f:
        json.dump(kek, f)

    if force:
        begin()
    else:
        main(showing_mode, showing_bird)


def multiplayer():
    screen = pygame.display.set_mode((width, height))
    force = False

    fitness = 0
    with open("nets.json") as f:
        nets = [Neural_Net(i) for i in json.load(f)["nets"]]
    with open("nets.json") as f:
        gen = json.load(f)["gen"]

    birds = [Bird(i) for i in range(1, len(nets) + 1)]

    bird = Bird(5)

    obst = Obstacle()

    gameover = False

    screen.blit(bg, (0, 0))

    birds[0].draw(screen)
    bird.draw(screen)
    obst.draw(screen)

    pygame.display.update()

    game_start = False

    while not game_start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameover = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_start = True
                elif event.key == pygame.K_ESCAPE:
                    force = True
                    game_start = True
                    gameover = True

    while not gameover:
        jumped = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                gameover = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    force = True
                    gameover = True
                    break
                if event.key == pygame.K_SPACE:
                    bird.jump()
                    jumped = True

        screen.blit(bg, (0, 0))
        for i in range(0, 1):
            if not birds[i].gameover:
                nets[i].set_values([-int(birds[i].y - (obst.heigh + 0.5 * height_of_obj_gape)),
                                    int(obst.x + 0.5 * width_of_obj - bird_start_pos)])

                birds[i].set_values([-int(birds[i].y - (obst.heigh + 0.5 * height_of_obj_gape)),
                                     int(obst.x + 0.5 * width_of_obj - bird_start_pos)])

                nets[i].update_values()
                if nets[i].neurons[nets[i].get_id(nets[i].layer_count - 1,
                                                  nets[i].layer_capacity[nets[i].layer_count - 1] - 1)].value >= 0.5:
                    birds[i].jump()

                if not birds[i].logic():
                    birds[i].fitnes = fitness
                    birds[i].gameover = True

                if obst == birds[i]:
                    birds[i].fitnes = fitness
                    birds[i].gameover = True

                birds[i].draw(screen)

        if jumped:
            nets[0].learn_with_backpropagation([[-int(bird.y - (obst.heigh + 0.5 * height_of_obj_gape)),
                                                 int(obst.x + 0.5 * width_of_obj - bird_start_pos)]], [[1]], 3)
        elif randint(0, 100) > 80:
            nets[0].learn_with_backpropagation([[-int(bird.y - (obst.heigh + 0.5 * height_of_obj_gape)),
                                                 int(obst.x + 0.5 * width_of_obj - bird_start_pos)]], [[0]], 1)

        if not bird.logic() or bird == obst:
            gameover = True
        bird.draw(screen)

        if not obst.logic():
            obst = Obstacle()
        obst.draw(screen)

        pygame.display.update()
        # pygame.time.wait(1)
        fitness += 1

    kek = {"gen": gen, "nets": []}
    for i in nets:
        kek["nets"].append(i.save_result())

    with open("nets.json", 'w') as f:
        json.dump(kek, f)

    if force:
        begin()
    else:
        pygame.time.delay(1000)
        pygame.draw.rect(screen, (255, 255, 255), (45, 150, 260, 100))
        if birds[0].gameover:
            score_text = myfont.render('YOU WIN', 0, (0, 0, 0))
            screen.blit(score_text, (100, 180))
        else:
            score_text = myfont.render('GAME OVER', 0, (0, 0, 0))
            screen.blit(score_text, (80, 180))

        pygame.display.update()

        while gameover:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    gameover = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        gameover = False
                    elif event.key == pygame.K_ESCAPE:
                        force = True
                        gameover = False
                        break
        multiplayer()


begin()
