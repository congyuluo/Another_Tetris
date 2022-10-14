import time

import pygame as pg
from tetris_game import tetris

game_window_size = (300, 600)
side_window_width = game_window_size[0] / 2
window_size = (game_window_size[0] + side_window_width, game_window_size[1])

# Refresh_rate
secs_per_drop = 0.8

if __name__ == "__main__":
    # Init game
    myGame = tetris(game_window_size, side_window_width)
    # myGame.board[2][19] = 1

    pg.init()
    window = pg.display.set_mode(window_size)
    pg.display.set_caption('Tetris')

    # Refresh counter
    last_drop_time = time.time()
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                break
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_LEFT:
                    myGame.input_respond('left')
                if event.key == pg.K_RIGHT:
                    myGame.input_respond('right')
                if event.key == pg.K_UP:
                    myGame.input_respond('up')
                if event.key == pg.K_DOWN:
                    myGame.input_respond('down')

        myGame.draw(window)

        if not myGame.game_respond():
            quit()

        if time.time() - last_drop_time > secs_per_drop:
            myGame.drop()
            last_drop_time = time.time()

        pg.display.update()