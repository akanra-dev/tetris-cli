#!/usr/bin/env python3
import curses
import time
import random

WIDTH = 10
HEIGHT = 20

SHAPES = [
    [[1, 1, 1, 1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[1, 0, 0], [1, 1, 1]],
    [[0, 0, 1], [1, 1, 1]],
    [[1, 1, 0], [0, 1, 1]],
    [[0, 1, 1], [1, 1, 0]]
]

def rotate(shape):
    return list(zip(*shape[::-1]))

def new_piece():
    idx = random.randrange(len(SHAPES))
    shape = SHAPES[idx]
    return {
        "shape": shape,
        "type": idx,
        "x": WIDTH // 2 - len(shape[0]) // 2,
        "y": 0
    }

def collision(board, piece, dx=0, dy=0, rotated=None):
    shape = rotated if rotated else piece["shape"]
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                nx = piece["x"] + x + dx
                ny = piece["y"] + y + dy
                if nx < 0 or nx >= WIDTH or ny < 0 or ny >= HEIGHT:
                    return True
    return False

def merge(board, piece):
    for y, row in enumerate(piece["shape"]):
        for x, cell in enumerate(row):
            if cell:
                board[piece["y"] + y][piece["x"] + x] = piece["type"] + 1

def clear_lines(board):
    new_board = []
    cleared = 0
    for row in board:
        if all(row):
            cleared += 1
        else:
            new_board.append(row)
    while len(new_board) < HEIGHT:
        new_board.insert(0, [0] * WIDTH)
    return new_board, cleared

def draw(stdscr, board, piece, score, level):
    stdscr.clear()

    stdscr.addstr(0, WIDTH * 2 + 3, f"Score: {score}")
    stdscr.addstr(1, WIDTH * 2 + 3, f"Level: {level}")

    for y in range(HEIGHT):
        for x in range(WIDTH):
            if board[y][x]:
                stdscr.addstr(y + 1, x * 2, "[]", curses.color_pair(board[y][x]))

    for y, row in enumerate(piece["shape"]):
        for x, cell in enumerate(row):
            if cell:
                stdscr.addstr(piece["y"] + y + 1, (piece["x"] + x) * 2, "[]",
                              curses.color_pair(piece["type"] + 1))
    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_MAGENTA, -1)
    curses.init_pair(4, curses.COLOR_GREEN, -1)
    curses.init_pair(5, curses.COLOR_RED, -1)
    curses.init_pair(6, curses.COLOR_BLUE, -1)
    curses.init_pair(7, curses.COLOR_WHITE, -1)
    stdscr.timeout(50)

    board = [[0] * WIDTH for _ in range(HEIGHT)]
    piece = new_piece()
    last_fall = time.time()

    score = 0
    level = 1
    lines_cleared_total = 0

    while True:
        fall_speed = max(0.1, 0.5 - (level - 1) * 0.05)

        if time.time() - last_fall > fall_speed:
            if not collision(board, piece, dy=1):
                piece["y"] += 1
            else:
                merge(board, piece)
                board, cleared = clear_lines(board)
                if cleared > 0:
                    score += cleared * 100
                    lines_cleared_total += cleared
                    level = 1 + lines_cleared_total // 5

                piece = new_piece()

                if collision(board, piece):
                    break

            last_fall = time.time()

        try:
            key = stdscr.getkey()
            if key == "a" and not collision(board, piece, dx=-1):
                piece["x"] -= 1
            elif key == "d" and not collision(board, piece, dx=1):
                piece["x"] += 1
            elif key == "s" and not collision(board, piece, dy=1):
                piece["y"] += 1
            elif key == "w":
                r = rotate(piece["shape"])
                if not collision(board, piece, rotated=r):
                    piece["shape"] = r
            elif key == "q":
                break
        except curses.error:
            pass

        draw(stdscr, board, piece, score, level)

    # GAME OVER SCREEN
    stdscr.nodelay(False)
    stdscr.clear()
    stdscr.addstr(HEIGHT // 2, WIDTH -3, "GAME OVER")
    stdscr.addstr(HEIGHT // 2 + 1, WIDTH - 5, f"Final Score: {score}")
    stdscr.addstr(HEIGHT // 2 + 3, WIDTH - 6, "Press any key...")
    stdscr.refresh()
    stdscr.getkey()

curses.wrapper(main)
