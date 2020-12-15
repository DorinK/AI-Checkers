# ===============================================================================
# Imports
# ===============================================================================

import abstract
from players import simple_player
from utils import MiniMaxWithAlphaBetaPruning, INFINITY, run_with_limited_time, ExceededTimeError
from checkers.consts import EM, PAWN_COLOR, KING_COLOR, OPPONENT_COLOR, MAX_TURNS_NO_JUMP, RP, RK, BK, MY_COLORS, \
    RED_PLAYER
import time
from collections import defaultdict

# ===============================================================================
# Globals
# ===============================================================================

PAWN_WEIGHT = 1
KING_WEIGHT = 1.5


# ===============================================================================
# Player
# ===============================================================================

class Player(simple_player.Player):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        simple_player.Player.__init__(self, setup_time, player_color, time_per_k_turns, k)

    def utility(self, state):     ### The simple player defeats him mercilessly :( ###

        if len(state.get_possible_moves()) == 0:
            return INFINITY if state.curr_player != self.color else -INFINITY
        if state.turns_since_last_jump >= MAX_TURNS_NO_JUMP:
            return 0

        opponent_color = OPPONENT_COLOR[self.color]

        opponent_pieces = 0
        opponent_kings = 0
        my_pieces = 0
        my_kings = 0
        opponent_pos_sum = 0
        my_pos_sum = 0

        for loc, loc_val in state.board.items():

            if loc_val in MY_COLORS[self.color]:
                my_pieces+=1
                if loc_val == KING_COLOR[self.color]:
                    my_kings += 0.5
                my_pos = evaluate_position(loc[1], loc[0])
                my_pos_sum += my_pos

                # Tried giving score according to if the player in the opponnent's half of the board
                # if loc_val == KING_COLOR[self.color]:
                #     my_kings += 0.5
                #     my_pos_sum += 10
                # else:
                #     if self.color == RED_PLAYER:
                #         my_pos = 7 if loc[0] >= 4 else 5
                #         my_pos_sum += my_pos
                #     else:
                #         my_pos = 7 if loc[0] <= 3 else 5
                #         my_pos_sum += my_pos

            else:
                opponent_pieces += 1
                if loc_val == KING_COLOR[opponent_color]:
                    opponent_kings += 0.5
                opponent_pos = evaluate_position(loc[1], loc[0])
                opponent_pos_sum += opponent_pos

                # Tried giving score according to if the opponnent in the playesr's half of the board
                # if loc_val == KING_COLOR[opponent_color]:
                #     opponent_kings += 0.5
                #     opponent_pos_sum+=10
                # else:
                #     if opponent_color == RED_PLAYER:
                #         opponent_pos = 7 if loc[0] >= 4 else 5
                #         opponent_pos_sum += opponent_pos
                #     else:
                #         opponent_pos = 7 if loc[0] <= 3 else 5
                #         opponent_pos_sum += opponent_pos

        piece_difference = opponent_pieces - my_pieces
        king_difference = opponent_kings - my_kings

        # if my_pieces == 0 and my_kings == 0:
        #     return -INFINITY
        #
        # if opponent_pieces == 0 and opponent_kings == 0:
        #     return INFINITY

        if my_pieces == 0:
            my_pieces = 0.00001

        avg_human_pos = my_pos_sum / my_pieces
        if opponent_pieces == 0:
            opponent_pieces = 0.00001

        avg_computer_pos = opponent_pos_sum / opponent_pieces
        avg_pos_diff = avg_computer_pos - avg_human_pos

        features = [piece_difference, king_difference, avg_pos_diff]
        weights = [100, 10, 1]  # tried different weights but it doesn't make a difference.

        board_utility = 0

        for f in range(len(features)):
            fw = features[f] * weights[f]
            board_utility += fw

        return board_utility

        # OLD UTILITY
        # my_u = ((PAWN_WEIGHT * piece_counts[PAWN_COLOR[self.color]]) +
        #         (KING_WEIGHT * piece_counts[KING_COLOR[self.color]]))
        # op_u = ((PAWN_WEIGHT * piece_counts[PAWN_COLOR[opponent_color]]) +
        #         (KING_WEIGHT * piece_counts[KING_COLOR[opponent_color]]))
        # if my_u == 0:
        #     # I have no tools left
        #     return -INFINITY
        # elif op_u == 0:
        #     # The opponent has no tools left
        #     return INFINITY
        # else:
        #     return my_u - op_u

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'better_h')


def evaluate_position(x , y):
    if x == 0 or x == 7 or y == 0 or y == 7:
        return 5
    else:
        return 3
