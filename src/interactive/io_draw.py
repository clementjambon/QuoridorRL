from interactive import CELL_PADDING, CELL_SIZE, INNER_CELL_SIZE, ACTION_DESCRIPTIONS, TEXT_COLOR, EMPTY_CELL_COLOR, PAWN_0_COLOR, PAWN_1_COLOR, WALL_THICKNESS, WALL_COLOR
from environment import QuoridorState, QuoridorConfig
import pygame as pg


def init_surfaces(screen: pg.Surface):
    # Background
    background = pg.Surface(screen.get_size())
    background = background.convert()
    background.fill((170, 238, 187))

    # Cell surface
    cell = pg.Surface((INNER_CELL_SIZE, INNER_CELL_SIZE))
    cell = cell.convert()
    cell.fill(EMPTY_CELL_COLOR)

    # Player 0 (white) pawn
    pawn_0 = pg.Surface((INNER_CELL_SIZE, INNER_CELL_SIZE))
    pawn_0 = pawn_0.convert()
    pawn_0.fill(PAWN_0_COLOR)

    # Player 1 (black) pawn
    pawn_1 = pg.Surface((INNER_CELL_SIZE, INNER_CELL_SIZE))
    pawn_1 = pawn_1.convert()
    pawn_1.fill(PAWN_1_COLOR)

    # Horizontal wall
    horizontal_wall = pg.Surface(
        (2 * INNER_CELL_SIZE + WALL_THICKNESS, WALL_THICKNESS))
    horizontal_wall = horizontal_wall.convert()
    horizontal_wall.fill(WALL_COLOR)

    # Vertical wall
    vertical_wall = pg.Surface(
        (WALL_THICKNESS, 2 * INNER_CELL_SIZE + WALL_THICKNESS))
    vertical_wall = vertical_wall.convert()
    vertical_wall.fill(WALL_COLOR)

    return background, cell, pawn_0, pawn_1, horizontal_wall, vertical_wall


def draw_gui(screen: pg.Surface, game_config: QuoridorConfig,
             state: QuoridorState, action_mode: int, done: bool) -> None:
    if pg.font:
        font = pg.font.Font(None, 64)
        player_text = font.render(f"Player {state.current_player} is playing",
                                  True, TEXT_COLOR)
        player_text_pos = (0, game_config.grid_size * CELL_SIZE)
        screen.blit(player_text, player_text_pos)

        action_text = font.render(
            f"Action: {ACTION_DESCRIPTIONS[action_mode]}", True, TEXT_COLOR)
        action_text_pos = (0, game_config.grid_size * CELL_SIZE + 64)
        screen.blit(action_text, action_text_pos)

        wall_text = font.render(
            f"P0 walls: {state.nb_walls[0]}/{game_config.max_walls} -- P1 walls: {state.nb_walls[1]}/{game_config.max_walls}",
            True, TEXT_COLOR)
        wall_text_pos = (0, game_config.grid_size * CELL_SIZE + 64 * 2)
        screen.blit(wall_text, wall_text_pos)

        command_font = pg.font.Font(None, 35)
        command_text = command_font.render(
            f"Command: click on space bar to change action mode", True,
            (128, 128, 128))
        command_text_pos = (0, game_config.grid_size * CELL_SIZE + 64 * 4)
        screen.blit(command_text, command_text_pos)

        if done:
            done_text = font.render(
                f"Game is over: player {state.winner} won!"
                if state.winner >= 0 else "Game is over: ended with a draw!",
                True, TEXT_COLOR)
            done_text_pos = (0, game_config.grid_size * CELL_SIZE + 64 * 3)
            screen.blit(done_text, done_text_pos)


def draw_board(screen: pg.Surface, game_config: QuoridorConfig,
               cell: pg.Surface) -> None:
    for i in range(game_config.grid_size):
        for j in range(game_config.grid_size):
            pixel_coord = (i * CELL_SIZE + CELL_PADDING,
                           j * CELL_SIZE + CELL_PADDING)
            screen.blit(cell, pixel_coord)


CC_COLOR_LIST = [(128, 0, 0), (0, 255, 0), (0, 255, 255), (138, 43, 226),
                 (220, 20, 60), (0, 255, 255), (255, 140, 0), (143, 188, 143),
                 (255, 20, 147), (255, 215, 0), (75, 0, 130), (46, 139, 87),
                 (0, 0, 128)]


def draw_walls(screen,
               game_config: QuoridorConfig,
               state: QuoridorState,
               horizontal_wall: pg.Surface,
               vertical_wall: pg.Surface,
               display_cc=False):
    # Draw walls
    for i in range(0, game_config.grid_size - 1):
        for j in range(0, game_config.grid_size - 1):
            color = WALL_COLOR
            if display_cc:
                color = CC_COLOR_LIST[state.ufind.get_wall_cc(
                    (i, j), state.walls[i, j]) % len(CC_COLOR_LIST)]
            # Draw horizontal wall (i.e along x)
            if (state.walls[i, j] == 0):
                draw_horizontal_wall(screen,
                                     horizontal_wall,
                                     i,
                                     j,
                                     color=color)
            # Draw vertical wall (i.e along y)
            elif (state.walls[i, j] == 1):  # Draw vertical wall
                draw_vertical_wall(screen, vertical_wall, i, j, color=color)


def draw_horizontal_wall(screen: pg.Surface,
                         horizontal_wall: pg.Surface,
                         i: int,
                         j: int,
                         color: pg.Color = WALL_COLOR) -> None:
    wall_position = (CELL_PADDING + i * CELL_SIZE,
                     CELL_PADDING + INNER_CELL_SIZE + CELL_SIZE * j)
    horizontal_wall.fill(color if color is not None else WALL_COLOR)
    screen.blit(horizontal_wall, wall_position)


def draw_vertical_wall(screen: pg.Surface,
                       vertical_wall: pg.Surface,
                       i: int,
                       j: int,
                       color: pg.Color = WALL_COLOR) -> None:
    wall_position = (CELL_PADDING + INNER_CELL_SIZE + CELL_SIZE * i,
                     CELL_PADDING + j * CELL_SIZE)
    vertical_wall.fill(color if color is not None else WALL_COLOR)
    screen.blit(vertical_wall, wall_position)


def draw_state(screen,
               game_config: QuoridorConfig,
               state: QuoridorState,
               pawn_0: pg.Surface,
               pawn_1: pg.Surface,
               horizontal_wall: pg.Surface,
               vertical_wall: pg.Surface,
               display_cc=False) -> None:
    # Draw pawn 0
    pawn_0_position = state.player_positions[0]
    pawn_0_position = (pawn_0_position[0] * CELL_SIZE + CELL_PADDING,
                       pawn_0_position[1] * CELL_SIZE + CELL_PADDING)
    screen.blit(pawn_0, pawn_0_position)
    # Draw pawn 1
    pawn_1_position = state.player_positions[1]
    pawn_1_position = (pawn_1_position[0] * CELL_SIZE + CELL_PADDING,
                       pawn_1_position[1] * CELL_SIZE + CELL_PADDING)
    screen.blit(pawn_1, pawn_1_position)

    # Draw walls
    draw_walls(screen, game_config, state, horizontal_wall, vertical_wall,
               display_cc)
