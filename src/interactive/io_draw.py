from interactive import CELL_PADDING, CELL_SIZE, INNER_CELL_SIZE, ACTION_DESCRIPTIONS, GRID_SIZE, TEXT_COLOR
from environment import QuoridorEnv
import pygame as pg


def draw_gui(screen: pg.Surface, environment: QuoridorEnv, action_mode: int,
             done: bool) -> None:
    if pg.font:
        font = pg.font.Font(None, 64)
        player_text = font.render(
            f"Player {environment.current_player} is playing", True,
            TEXT_COLOR)
        player_text_pos = (0, GRID_SIZE * CELL_SIZE)
        screen.blit(player_text, player_text_pos)

        action_text = font.render(
            f"Action: {ACTION_DESCRIPTIONS[action_mode]}", True, TEXT_COLOR)
        action_text_pos = (0, GRID_SIZE * CELL_SIZE + 64)
        screen.blit(action_text, action_text_pos)

        command_font = pg.font.Font(None, 35)
        command_text = command_font.render(
            "Command: click on space bar to change action mode", True,
            (128, 128, 128))
        command_text_pos = (0, GRID_SIZE * CELL_SIZE + 120)
        screen.blit(command_text, command_text_pos)

        #TODO : add number of walls left for each player
        #TODO : add warning when no more walls and remove possible actions (right now wrong msg "cannot move player")

        if done:
            done_text = font.render(
                f"Game is over: player {environment.state.get_opponent(environment.current_player)} won!",
                True, TEXT_COLOR)
            done_text_pos = (0, GRID_SIZE * CELL_SIZE + 64 * 2)
            screen.blit(done_text, done_text_pos)


def draw_board(screen: pg.Surface, cell: pg.Surface) -> None:
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            pixel_coord = (i * CELL_SIZE + CELL_PADDING,
                           j * CELL_SIZE + CELL_PADDING)
            screen.blit(cell, pixel_coord)


def draw_horizontal_wall(screen: pg.Surface, horizontal_wall: pg.Surface,
                         i: int, j: int) -> None:
    wall_position = (CELL_PADDING + i * CELL_SIZE,
                     CELL_PADDING + INNER_CELL_SIZE + CELL_SIZE * j)
    screen.blit(horizontal_wall, wall_position)


def draw_vertical_wall(screen: pg.Surface, vertical_wall: pg.Surface, i: int,
                       j: int) -> None:
    wall_position = (CELL_PADDING + INNER_CELL_SIZE + CELL_SIZE * i,
                     CELL_PADDING + j * CELL_SIZE)
    screen.blit(vertical_wall, wall_position)


def draw_state(screen, environment: QuoridorEnv, pawn_0: pg.Surface,
               pawn_1: pg.Surface, horizontal_wall: pg.Surface,
               vertical_wall: pg.Surface) -> None:
    # Draw pawn 0
    pawn_0_position = environment.state.player_positions[0]
    pawn_0_position = (pawn_0_position[0] * CELL_SIZE + CELL_PADDING,
                       pawn_0_position[1] * CELL_SIZE + CELL_PADDING)
    screen.blit(pawn_0, pawn_0_position)
    # Draw pawn 1
    pawn_1_position = environment.state.player_positions[1]
    pawn_1_position = (pawn_1_position[0] * CELL_SIZE + CELL_PADDING,
                       pawn_1_position[1] * CELL_SIZE + CELL_PADDING)
    screen.blit(pawn_1, pawn_1_position)

    # Draw walls
    for i in range(0, GRID_SIZE - 1):
        for j in range(0, GRID_SIZE - 1):
            # Draw horizontal wall (i.e along x)
            if (environment.state.walls[i, j] == 0):
                draw_horizontal_wall(screen, horizontal_wall, i, j)
            # Draw vertical wall (i.e along y)
            elif (environment.state.walls[i, j] == 1):  # Draw vertical wall
                draw_vertical_wall(screen, vertical_wall, i, j)
