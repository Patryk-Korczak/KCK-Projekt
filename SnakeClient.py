import random
from math import floor
from threading import Thread

import pygame
import socket
import pickle
import time


# This is host file for Multi Snake game. Run this file first. There's 5 seconds timeout allowing to start
# SnakeClient in time.

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
        self.apple_x = 510
        self.apple_y = 380


class AsyncHost(Thread):
    def __init__(self):
        super().__init__()

    def run(self):

        host = "localhost"
        port = 8000
        my_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_server.connect((host, port))
        while True:
            try:
                data_received = my_server.recv(4096)
                if data_received == b'':
                    break
                else:
                    self.datareceived = pickle.loads(data_received)
                data_to_send = pickle.dumps(my_snake)
                my_server.send(data_to_send)

            except Exception as expt:
                print(expt)

    def get_data(self):
        return self.datareceived


my_snake = Snake()
my_snake.color = (0, 255, 0)  # green
my_snake.x = 760
my_snake.y = 380

display_width = 1020
display_height = 760
server = AsyncHost()
server.start()
time.sleep(5)

enemy_snake = server.get_data()
pygame.init()
display = pygame.display.set_mode((display_width, display_height))
pygame.display.update()
pygame.display.set_caption('MultiSnake - Client')
game_over = False
block_length = 10  # 10 pixels for 1 block of snake
clock = pygame.time.Clock()
game_speed = 12

def new_apple():
    my_snake.apple_x = round(random.randrange(0, display_width - block_length) / 10.0) * 10.0
    my_snake.apple_y = round(random.randrange(0, display_width - block_length) / 10.0) * 10.0

while not game_over:
    enemy_snake = server.get_data()  # update enemy snake position
    my_snake.apple_y = enemy_snake.apple_y
    my_snake.apple_x = enemy_snake.apple_x
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



    display.fill((255, 255, 255))  # clear display with whit color
    if my_snake.alive:
        for x in my_snake.snake_body:
            pygame.draw.rect(display, my_snake.color, [x[0], x[1], block_length, block_length])
    if enemy_snake.alive:
        for x in enemy_snake.snake_body:
            pygame.draw.rect(display, enemy_snake.color, [x[0], x[1], block_length, block_length])
    pygame.draw.rect(display, (255, 0, 0), [floor(enemy_snake.apple_x), floor(enemy_snake.apple_y), block_length, block_length])
    if not my_snake.alive and not enemy_snake.alive:
        game_over = True

    if my_snake.x == my_snake.apple_x and my_snake.y == my_snake.apple_y:
        my_snake.length += 1
        print("Your snake ate apple...")
        new_apple()

    if enemy_snake.x == my_snake.apple_x and enemy_snake.y == my_snake.apple_y:
        print("Enemy snake ate apple...")
        new_apple()

    pygame.display.update()
    clock.tick(game_speed)
