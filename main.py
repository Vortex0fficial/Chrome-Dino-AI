import pygame
import os
import random
import sys
import neat
import math
import time

pygame.init()
WIN_HEIGHT = 600
WIN_WIDTH = 1100
WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("NEAT DESTROYS CHROME DINO GAME")

RUNNING = [pygame.transform.scale2x(pygame.image.load(os.path.join("Images/dino", "run1.png"))),
           pygame.transform.scale2x(pygame.image.load(os.path.join("Images/dino", "run2.png")))]

JUMPING = pygame.transform.scale2x(pygame.image.load(os.path.join("Images/dino", "jump.png")))

BG = pygame.transform.scale_by(pygame.image.load(os.path.join("Images/floor", "floor.png")), (12, 12))

CACTUS = pygame.transform.scale_by(pygame.image.load(os.path.join("Images/cacti", "bettercac.png")), (1, 1))

FONT = pygame.font.Font('freesansbold.ttf', 20)


class Dino:
    X_POS = 20
    Y_POS = 270

    HIT_BOX_OFFSET_X, HIT_BOX_OFFSET_Y = 100, 100
    JUMP_VEL = 8.5

    def __init__(self, img=RUNNING[0]):
        self.image = img
        self.dino_run = True
        self.dino_jump = False
        self.jump_vel = self.JUMP_VEL
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, img.get_width() / 2, img.get_height() / 2)
        self.step_index = 0
        self.score = 0

    def update(self):
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()
        if self.step_index >= 10:
            self.step_index = 0

    def jump(self):
        self.image = JUMPING
        if self.dino_jump:
            self.rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel <= -self.JUMP_VEL:
            self.dino_jump = False
            self.dino_run = True
            self.jump_vel = self.JUMP_VEL

    def run(self):
        self.image = RUNNING[self.step_index // 5]
        self.rect.x = self.X_POS + self.HIT_BOX_OFFSET_X
        self.rect.y = self.Y_POS + self.HIT_BOX_OFFSET_Y
        self.step_index += 1

    def draw(self, win):
        win.blit(self.image, (self.rect.x - self.HIT_BOX_OFFSET_X / 2, self.rect.y - self.HIT_BOX_OFFSET_Y / 2))
        pygame.draw.rect(win, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)
        for obstaclee in obstacles:
            pygame.draw.line(win, self.color, (self.rect.x + 54, self.rect.y + 12), obstaclee.rect.center, 2)


class Obstacle:
    HIT_BOX_OFFSET_X, HIT_BOX_OFFSET_Y = 0, 0

    def __init__(self, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = WIN_WIDTH + self.HIT_BOX_OFFSET_X

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, win):
        win.blit(self.image, (self.rect.x - self.HIT_BOX_OFFSET_X, self.rect.y - self.HIT_BOX_OFFSET_Y))
        pygame.draw.rect(win, (0, 0, 0), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)


class Cactus(Obstacle):
    def __init__(self, image):
        super().__init__(image)
        self.rect.y = 375


def remove(index):
    dinos.pop(index)
    ge.pop(index)
    nets.pop(index)


def distance(pos_a, pos_b):
    dx = pos_a[0] - pos_b[0]
    dy = pos_a[1] - pos_b[1]
    return math.sqrt(dx ** 2 + dy ** 2)


class Ground:
    global game_speed
    WIDTH = BG.get_width()

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = WIN_WIDTH

    def move(self):
        self.x1 -= game_speed
        self.x2 -= game_speed

        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(BG, (self.x1, self.y))
        win.blit(BG, (self.x2, self.y))


global best_score
best_score = 0


def eval_genomes(genomes, config):
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles, dinos, ge, nets, obstacle
    clock = pygame.time.Clock()
    points = 0

    obstacles = []
    dinos = []
    ge = []
    nets = []

    ground = Ground(-630)

    x_pos_bg = 0
    y_pos_bg = 380
    game_speed = 20

    for genome_id, genome in genomes:
        dinos.append(Dino())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    def score():
        global points, game_speed, best_score
        points += 1
        if points % 100 == 0:
            game_speed += 1
        for ie, dinoe in enumerate(dinos):
            if points % 100 == 0:
                ge[ie].fitness += 1
                dinoe.score += 1
            if points > best_score:
                best_score = points

        text = FONT.render(f'Points: {str(points)}', True, (0, 0, 0))
        best_score_text = FONT.render(f'Best Score: {str(best_score)}', True, (0, 0, 0))
        WIN.blit(text, (850, 20))
        WIN.blit(best_score_text, (850, 60))

    def statistics(win):
        global dinos, game_speed, ge
        text_1 = FONT.render(f'Dinosaurs Alive:  {str(len(dinos))}', True, (0, 0, 0))
        text_2 = FONT.render(f'Generation:  {pop.generation + 1}', True, (0, 0, 0))
        text_3 = FONT.render(f'Game Speed:  {str(game_speed)}', True, (0, 0, 0))

        win.blit(text_1, (50, 20))
        win.blit(text_2, (50, 60))
        win.blit(text_3, (50, 100))

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        WIN.fill((255, 255, 255))

        for dino in dinos:
            dino.update()
            dino.draw(WIN)

        statistics(WIN)
        score()
        ground.move()
        ground.draw(WIN)

        if len(dinos) == 0:
            time.sleep(2)
            break

        if len(obstacles) == 0:
            obstacles.append(Cactus(CACTUS))

        for obstacle in obstacles:
            obstacle.draw(WIN)
            obstacle.update()
            for i, dino in enumerate(dinos):
                if dino.rect.colliderect(obstacle.rect):
                    ge[i].fitness -= 1
                    remove(i)

        for i, dino in enumerate(dinos):
            output = nets[i].activate((dino.rect.y, distance((dino.rect.x, dino.rect.y), obstacle.rect.midtop), game_speed))
            if output[0] > 0.5 and dino.rect.y == dino.Y_POS + 100:
                dino.dino_jump = True
                dino.dino_run = False

        clock.tick(30)
        pygame.display.update()


def rune(config_pathe):
    global pop
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_pathe)
    pop = neat.Population(config)
    pop.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    rune(config_path)
