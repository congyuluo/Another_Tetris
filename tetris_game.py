from random import randint
from copy import deepcopy

import numpy as np
import pygame as pg

# Style
line_colour = (192, 198, 211)
game_background_colour = (255, 255, 255)
game_side_window_colour = (255, 255, 255)
stationary_brick_colour = (60, 63, 65)
moving_block_colour = (203, 43, 41)
waitlist_colour = (86, 187, 191)
ghost_colour = (155, 96, 48)


def rot_brick(shape: [[]], times: int) -> [[]]:
    for _ in range(times):
        shape = np.rot90(shape)
    return shape


class brick:
    brick_names = ['i', 'j', 'l', 'o', 's', 't', 'z']
    bricks = {'i': [[1, 1, 1, 1]], 'j': [[1, 0, 0], [1, 1, 1]], 'l': [[0, 0, 1], [1, 1, 1]], 'o': [[1, 1], [1, 1]], 's':
        [[0, 1, 1], [1, 1, 0]], 't': [[0, 1, 0], [1, 1, 1]], 'z': [[1, 1, 0], [0, 1, 1]]}

    def __init__(self, shape="random", orientation="random"):
        if shape == "random":
            self.shape = brick.bricks[brick.brick_names[randint(0, len(brick.brick_names) - 1)]]
        else:
            self.shape = brick.bricks[shape]

        if orientation == "random":
            orientation = randint(0, 3)

        # 0 for original orientation
        self.shape = rot_brick(self.shape, orientation)
        self.top_left_coordinate = [0, -1 * len(self.shape[0])]

    def match_position(self, game_width: int):
        """Find a random position to insert the brick"""
        shape_width = len(self.shape)
        shift = randint(0, game_width - shape_width)
        self.top_left_coordinate[0] += shift

    def descend(self):
        """Descends the brick by one unit"""
        self.top_left_coordinate[1] += 1


class tetris:
    def __init__(self, window_size: tuple, side_window_width: int, width=10, height=20, waitlist_len=3):
        if not (window_size[0] / width) == (window_size[1] / height):
            raise AttributeError("None Square brick size. Window size ratio mismatch")
        self.window_size = window_size
        self.side_width = side_window_width
        self.width, self.height = width, height
        # Game variables
        self.waitlist_len = waitlist_len
        self.current_brick = brick()
        self.current_brick.match_position(self.width)
        self.brick_waitlist = []
        self.board = [[0 for _ in range(self.height)] for _ in range(self.width)]
        # Generate initial waitlist
        for _ in range(self.waitlist_len):
            self.waitlist_generate()

    def waitlist_generate(self):
        """Generates a new random block in the waitlist"""
        temp = brick()
        temp.match_position(self.width)
        self.brick_waitlist.append(temp)

    def check_brick_landed(self, brick: brick) -> bool:
        """Checks if the current falling brick has landed"""
        brick_height = len(brick.shape[0])
        if brick.top_left_coordinate[1] + brick_height + 1 > self.height:
            return True
        for x, row in enumerate(brick.shape):
            for y, pixel in enumerate(row):
                if pixel == 1 and y + brick.top_left_coordinate[1] > -1:
                    if self.board[x + brick.top_left_coordinate[0]][y + brick.top_left_coordinate[1] + 1] == 1:
                        return True
        return False

    def input_respond(self, inp: str):
        """Respond to keyboard input"""
        # Positional movement
        if inp == 'left':
            self.current_brick.top_left_coordinate[0] -= 1
        elif inp == 'right':
            self.current_brick.top_left_coordinate[0] += 1
        # Rotational movement
        elif inp == 'up':
            self.current_brick.shape = rot_brick(self.current_brick.shape, 1)
            while not (self.current_brick.top_left_coordinate[0] > -1):
                self.current_brick.top_left_coordinate[0] += 1
            while not (self.current_brick.top_left_coordinate[0] + len(self.current_brick.shape) <= self.width):
                self.current_brick.top_left_coordinate[0] -= 1
            # Revert operation if rotation causes vertical collision
            if self.check_brick_landed(self.current_brick):
                self.current_brick.shape = rot_brick(self.current_brick.shape, 3)
        # Artificial drop
        elif inp == 'down':
            while not self.check_brick_landed(self.current_brick):
                self.drop()

        while not (self.current_brick.top_left_coordinate[0] > -1):
            self.current_brick.top_left_coordinate[0] += 1
        while not (self.current_brick.top_left_coordinate[0] + len(self.current_brick.shape) <= self.width):
            self.current_brick.top_left_coordinate[0] -= 1

    def game_respond(self) -> int:
        """Handle brick conversion, line deletion, and end game"""
        # Brick conversion
        if self.check_brick_landed(self.current_brick):
            # Check for end game
            for x, row in enumerate(self.current_brick.shape):
                for y, pixel in enumerate(row):
                    if pixel == 1 and y + self.current_brick.top_left_coordinate[1] < 0:
                        return 0
            # Add to static board
            for x in range(len(self.current_brick.shape)):
                for y in range(len(self.current_brick.shape[0])):
                    if self.current_brick.shape[x][y] == 1 and y + self.current_brick.top_left_coordinate[1] >= 0:
                        self.board[x + self.current_brick.top_left_coordinate[0]][
                            y + self.current_brick.top_left_coordinate[1]] = 1
            # Use next brick
            self.current_brick = self.brick_waitlist[0]
            self.brick_waitlist = self.brick_waitlist[1:]
            self.waitlist_generate()
        # Line deletion
        for i in range(self.height):
            # If current line is empty, shift previous lines down
            if not 0 in [self.board[x][i] for x in range(self.width)]:
                for transfer_line_index in range(i - 1, -1, -1):
                    for transfer_elem_index in range(self.width):
                        self.board[transfer_elem_index][transfer_line_index + 1] = self.board[transfer_elem_index][
                            transfer_line_index]
                for transfer_elem_index in range(self.width):
                    self.board[0][transfer_elem_index] = 0
        return 1

    def drop(self):
        """Drops the current active object"""
        if not self.check_brick_landed(self.current_brick):
            self.current_brick.descend()

    def draw(self, window, draw_ghost=True):
        # Draw game background
        pg.draw.rect(window, game_background_colour, (0, 0, self.window_size[0], self.window_size[1]), 0)

        # Draw side window background
        pg.draw.rect(window, game_background_colour,
                     (self.window_size[0], 0, self.window_size[0] + self.side_width, self.window_size[1]), 0)

        # Draw stationary blocks
        brick_size = (self.window_size[0] / self.width)
        for x in range(self.width):
            for y in range(self.height):
                if self.board[x][y] == 1:
                    pg.draw.rect(window, stationary_brick_colour,
                                 (x * brick_size, y * brick_size, brick_size, brick_size), 0)

        # Draw ghost
        if draw_ghost:
            ghost = deepcopy(self.current_brick)
            # Decend ghost brick
            while not self.check_brick_landed(ghost):
                ghost.descend()
            for x, row in enumerate(self.current_brick.shape):
                for y, pixel in enumerate(row):
                    if pixel == 1:
                        pg.draw.rect(window, ghost_colour,
                                     ((x + ghost.top_left_coordinate[0]) * brick_size,
                                      (y + ghost.top_left_coordinate[1]) * brick_size, brick_size,
                                      brick_size), 0)

        # Draw moving blocks
        for x, row in enumerate(self.current_brick.shape):
            for y, pixel in enumerate(row):
                if pixel == 1:
                    pg.draw.rect(window, moving_block_colour,
                                 ((x + self.current_brick.top_left_coordinate[0]) * brick_size,
                                  (y + self.current_brick.top_left_coordinate[1]) * brick_size, brick_size, brick_size),
                                 0)

        # Draw grids
        for x in range(0, self.window_size[1], int(self.window_size[1] / self.height)):
            pg.draw.line(window, line_colour, (0, x), (self.window_size[0], x), 1)
        # Draw grids
        for y in range(0, self.window_size[0], int(self.window_size[0] / self.width)):
            pg.draw.line(window, line_colour, (y, 0), (y, self.window_size[1]), 1)

        # Draw waitlist
        begin_y = brick_size
        for elem in self.brick_waitlist:
            elem_width = len(elem.shape) * brick_size
            elem_height = len(elem.shape[0]) * brick_size
            begin_x = self.window_size[0] + ((self.side_width - elem_width) / 2)
            for x, row in enumerate(elem.shape):
                for y, pixel in enumerate(row):
                    if pixel == 1:
                        pg.draw.rect(window, waitlist_colour,
                                     (begin_x + x * brick_size,
                                      begin_y + y * brick_size, brick_size,
                                      brick_size), 2)
            begin_y += elem_height + brick_size
