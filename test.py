from tetris_game import tetris, brick

b = brick(shape='i', orientation=2)
b.match_position(10)
print(b.top_left_coordinate)
