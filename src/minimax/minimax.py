import copy
from board_graph import BoardGraph
from quoridor_env import QuoridorEnv
from quoridor_state import QuoridorState


def minimax(env: QuoridorEnv, state: QuoridorState, depth: int,
            is_maximizing: bool):
    if depth == 2:
        f1 = position_feature(state, state.current_player)
        f2 = position_difference(env, state)
        f3 = move_to_next_col_feature(
            state, state.current_player)  #min_Mymove_next_col
        f4 = move_to_next_col_feature(
            state,
            env.get_opponent(state.current_player))  #max_Advmove_next_col
        score = f1 + f2 + f3 - f4
        return score

    if is_maximizing:
        best_score = float('-inf')
        copy_state = copy.deepcopy(state)
        copy_env = copy.deepcopy(env)
        #maximizing : current player
        list_actions = copy_env.get_possible_actions(copy_state) 
        for action in list_actions:
            copy_env.actNoCopy(copy_state, action)
            score = minimax(copy_env, copy_state, depth + 1, False)
            best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('-inf')
        copy_state = copy.deepcopy(state)
        copy_env = copy.deepcopy(env)
        #minimizing : opponent
        #copy_state.current_player = (state.current_player + 1) % env.nb_players
        list_actions =  env.get_possible_actions(copy_state)  
        for action in list_actions:
            copy_env.actNoCopy(copy_state, action)
            score = minimax(copy_env, copy_state, depth + 1, True)
            best_score = min(score, best_score)
        return best_score

def position_feature(state: QuoridorState, player_idx: int) -> int:
    """
    the simplest evaluation features is the number of columns that
    the pawn is away from his base line column
    if the pawn is on his base line, the value is 0. 
    If the pawn is on the goal line, the value is 8.
    """
    coords = state.player_positions[state.current_player]
    if player_idx == 0:
        return coords[0]  #rows and cols are strangely inversed
    else:
        return state.grid_size - 1 - coords[0]


def position_difference(env: QuoridorEnv, state: QuoridorState) -> int:
    """
    This feature returns the difference between the position feature
    of the Max player and the position feature of the Min player.
    It actually indicates how good your progress is compared to the opponent’s progress.
    """
    return position_feature(state, state.current_player) - position_feature(
        state, env.get_opponent())


def move_to_next_col_feature(state: QuoridorState, player_idx: int) -> int:
    """
        2 features can be derived : 
        • MINIMIZE nb of moves to next for current player (attacking move)
        • MAXIMIZE nb of moves for adversary player (defensive)
        each player will try to place fences in such a way that his opponent has to
        take as many steps as possible to get to his goal. To achieve this, 
        the fences have to be placed so that the opponent has to move up and down the board.
        This feature calculates the minimum number of steps that have to be taken to reach the next column
        A small amount of steps has to give a higher evaluation. 
        So the number of steps, of the Max player to the next column, 
        is raised by the power of −1.
        """

    board = BoardGraph(state.walls)
    player_position = state.player_positions[player_idx]

    parents_map, node_costs = board.dijkstra(player_position)

    if player_idx == 0:
        next_col = player_position[0] + 1
    else:
        next_col = player_position[0] - 1

    #get the tiles nb of the next column
    vertices_next_col = []
    for i in range(state.grid_size):
        vertices_next_col.append(next_col * state.grid_size + i)

    #find cost of closest tile in next col
    cost = float('inf')
    for target in vertices_next_col:
        if node_costs[target] < cost:
            cost = node_costs[target]
    return pow(cost, -1)
