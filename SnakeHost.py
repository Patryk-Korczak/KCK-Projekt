import random
from math import floor
from threading import Thread

import pygame
import socket
import pickle
import time
import pygame.freetype


# This is host file for Multi Snake game. Run this file first.

class Snake(object):
    def __init__(self):
        self.color = 0  # Color of snake
        self.x = 0  # Starting width
        self.y = 0  # Starting height
        self.x_change = 0  # Change of width while moving
        self.y_change = 0  # Change of height while moving
        self.snake_body = []  # List containing snake position
        self.length = 1  # Snake length
        self.alive = True  # is player still in the game
        self.apple_x = 510  # apple position x
        self.apple_y = 380  # apple position y


class AsyncHost(Thread):
    def __init__(self):
        super().__init__()

    def run(self):

        host = "localhost"
        port = 8000
        my_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_server.bind((host, port))
        my_server.listen()
        conn, addr = my_server.accept()
        while True:
            try:
                data_to_send = pickle.dumps(my_snake)
                conn.send(data_to_send)
                data_received = conn.recv(4096)
                if data_received == b'':
                    break
                else:
                    self.datareceived = pickle.loads(data_received)
            except Exception as expt:
                print(expt)

    def get_data(self):
        return self.datareceived


my_snake = Snake()
my_snake.color = (0, 0, 150)
my_snake.x = 250
my_snake.y = 380

display_width = 1020
display_height = 760
server = AsyncHost()
server.setDaemon(True)
server.start()
time.sleep(5)

enemy_snake = server.get_data()
pygame.init()
pygame.mixer.init()
apple_effect = pygame.mixer.Sound('sounds/apple.wav')
apple_effect.set_volume(0.05)
lost_effect = pygame.mixer.Sound('sounds/lost.wav')
lost_effect.set_volume(0.05)
display = pygame.display.set_mode((display_width, display_height))
pygame.display.update()
pygame.display.set_caption('MultiSnake - Host')
game_over = False
update_on_death = True  # flag to make sure player values on death only get updated once
block_length = 10  # 10 pixels for 1 block of snake
clock = pygame.time.Clock()
game_speed = 30
background = pygame.image.load('resources/game_background.png')
apple_image = pygame.image.load('resources/apple.png')
FONT = pygame.freetype.SysFont('Microsoft Sans Serif', 32)
pygame.mixer_music.load('sounds/background_music.wav')
pygame.mixer_music.set_volume(0.1)
pygame.mixer_music.play(-1)
max_length = display_width/10 * display_height/10


def new_apple():
    my_snake.apple_x = round(random.randrange(0, display_width - block_length) / 10.0) * 10.0
    my_snake.apple_y = round(random.randrange(0, display_height - block_length) / 10.0) * 10.0


def print_score():
    text = 'MultiSnake Current Score: ' + str(my_snake.length - 1) + ' Enemy Score: ' + str(enemy_snake.length - 1)
    pygame.display.set_caption(text)


while not game_over:

    enemy_snake = server.get_data()  # update enemy snake position

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_over = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                my_snake.x_change = block_length
                my_snake.y_change = 0
            if event.key == pygame.K_LEFT:
                my_snake.x_change = -block_length
                my_snake.y_change = 0
            if event.key == pygame.K_DOWN:
                my_snake.x_change = 0
                my_snake.y_change = block_length
            if event.key == pygame.K_UP:
                my_snake.x_change = 0
                my_snake.y_change = -block_length

    if my_snake.x > display_width or my_snake.x < 0 or my_snake.y > display_height or my_snake.y < 0:
        my_snake.alive = False  # wrap this into function

    print_score()

    my_snake.x += my_snake.x_change
    my_snake.y += my_snake.y_change

    my_snake_top = []
    my_snake_top.append(my_snake.x)
    my_snake_top.append(my_snake.y)
    my_snake.snake_body.append(my_snake_top)
    if len(my_snake.snake_body) > my_snake.length:
        del my_snake.snake_body[0]

    for x in my_snake.snake_body[:-1]:
        if x == my_snake_top:
            my_snake.alive = False

    for x in enemy_snake.snake_body[:]:
        if x == my_snake_top:
            my_snake.alive = False

    display.fill((255, 255, 255))  # clear display with whit color
    display.blit(background, (0, 0))
    display.blit(apple_image, (floor(enemy_snake.apple_x), floor(enemy_snake.apple_y)))
    if my_snake.alive:
        for x in my_snake.snake_body:
            pygame.draw.rect(display, my_snake.color, [x[0], x[1], block_length, block_length])
    if enemy_snake.alive:
        for x in enemy_snake.snake_body:
            pygame.draw.rect(display, enemy_snake.color, [x[0], x[1], block_length, block_length])

    if not my_snake.alive and not enemy_snake.alive:
        game_over = True
        pygame.display.update()
        display.fill((255, 255, 255))  # clear display with white color
        display.blit(background, (0, 0))
        FONT.render_to(display, (10, 50),
                       'Game over! Your score: ' + str(my_snake.length - 1) + ' Enemy score: ' + str(
                           enemy_snake.length - 1),
                       (255, 0, 0))
        FONT.render_to(display, (10, 100), 'Press SPACE to exit...', (255, 0, 0))

    if my_snake.x == my_snake.apple_x and my_snake.y == my_snake.apple_y:
        my_snake.length += 1
        apple_effect.play()
        new_apple()

    if enemy_snake.x == my_snake.apple_x and enemy_snake.y == my_snake.apple_y:
        new_apple()

    if my_snake.length + enemy_snake.length == max_length:
        FONT.render_to(display, (10, 50),
                       'YOU WON! Your score: ' + str(my_snake.length - 1) + ' Enemy score: ' + str(
                           enemy_snake.length - 1),
                       (255, 0, 0))
        FONT.render_to(display, (10, 100), 'Press SPACE to exit...', (255, 0, 0))

    if not my_snake.alive:
        my_snake.snake_body.clear()
        my_snake.x = 1
        my_snake.y = 1
        if enemy_snake.alive:
            FONT.render_to(display, (10, 10), 'You lost! Your score: ' + str(my_snake.length - 1), (255, 0, 0))
        if update_on_death:
            pygame.mixer_music.pause()
            lost_effect.play()
            update_on_death = False

    pygame.display.update()
    clock.tick(game_speed)

while game_over:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pygame.quit()
                quit()
