# ===============================================================================
# Imports
# ===============================================================================

import abstract
import math
from players import simple_player
from utils import MiniMaxWithAlphaBetaPruning, INFINITY, run_with_limited_time, ExceededTimeError
from checkers.consts import EM, PAWN_COLOR, KING_COLOR, OPPONENT_COLOR, MAX_TURNS_NO_JUMP, RP, RK, BK, MY_COLORS, \
    RED_PLAYER, BACK_ROW, BOARD_ROWS
import time
from collections import defaultdict

# ===============================================================================
# Globals
# ===============================================================================

PAWN_WEIGHT = 1
KING_WEIGHT = 1.5
MIN_DEEPENING_DEPTH = 5



# ===============================================================================
# Player
# ===============================================================================

"""
This class implements the improved_better player.
This player has both an advanced utility calculation, a time management logic that saves time for future moves and
a selective deepening criterion that forces the minmax algorithm to resume the search in cases the next move is a 
capture - Even if the depth limit was already reached
"""
class Player(simple_player.Player):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        simple_player.Player.__init__(self, setup_time, player_color, time_per_k_turns, k)

    """
    This method implements the utility calculation of the improved_better player. The utility function gets into account
    4 types of factors:
    1. Difference in amount of pieces of both players
    2. Difference in amount of kings of both players
    3. Difference in a score that is calculated for each player's pieces based on their location, while boosting strategic
    locations (See explanation in other function)
    4. A score distance that is calculated from the player's kings and the opponent's pieces. This score is used for either
    moving the player's kings closer to the opponent's pieces in case the player has kings advantage, ot moving the 
    player's kings away from opponent's pieces in case the opponent has kings advantage
    """
    def utility(self, state):
        if len(state.get_possible_moves()) == 0:
            return INFINITY if state.curr_player != self.color else -INFINITY
        if state.turns_since_last_jump >= MAX_TURNS_NO_JUMP:
            return 0

        piece_counts = defaultdict(lambda: 0)   # A dictionary that will hold the counts of each type of piece
        piece_locs = defaultdict(lambda: [])    # A dictionary that holds the list of locations of each type of piece
        for loc, loc_val in state.board.items():
            if loc_val != EM:   #   Current location is not empty
                piece_counts[loc_val] += 1  # Increment amount of current piece type
                piece_locs[loc_val].append(loc) # Add the location of current piece

        # Get opponent's color
        opponent_color = OPPONENT_COLOR[self.color]

        opponent_pos_sum = 0
        my_pos_sum = 0
        my_total_king_dist = 0

        # Count amount of pieces (Total piece count of myself/opponent's, Kings count of myself/opponent's)
        my_pieces = piece_counts[PAWN_COLOR[self.color]] + piece_counts[KING_COLOR[self.color]]
        opponent_pieces = piece_counts[PAWN_COLOR[opponent_color]] + piece_counts[KING_COLOR[opponent_color]]
        my_kings = piece_counts[KING_COLOR[self.color]]
        opponent_kings = piece_counts[KING_COLOR[opponent_color]]

        for loc, loc_val in state.board.items():    # Iterate through all location on the board
            if loc_val != EM:  # If current location is not empty
                if loc_val in MY_COLORS[self.color]:  # This location contains my color
                    # Evaluate utility of current location - Give boost to strategic locations
                    my_pos = self.evaluate_position(loc[1], loc[0], loc_val == KING_COLOR[self.color], piece_counts[PAWN_COLOR[opponent_color]],self.color)
                    my_pos_sum += my_pos  # Sum utility by positions
                    if loc_val == KING_COLOR[self.color]:   # Current piece is a king
                        # Calculate distances factor of all kings from all of opponent's pieces
                        dist = self.calculate_distance(loc, piece_locs[KING_COLOR[opponent_color]])
                        dist += self.calculate_distance(loc, piece_locs[PAWN_COLOR[opponent_color]])
                        my_total_king_dist += dist

                else:  # This location contains opponent's color
                    # Evaluate utility of current location - Give boost to strategic locations
                    opponent_pos = self.evaluate_position(loc[1], loc[0], loc_val == KING_COLOR[opponent_color], piece_counts[PAWN_COLOR[self.color]],opponent_color)
                    opponent_pos_sum += opponent_pos  # Give boost to strategic locations

        # Calculate total pieces difference and total kings difference
        piece_difference = my_pieces - opponent_pieces
        king_difference = my_kings - opponent_kings

        if my_pieces == 0 and my_kings == 0:
            return -INFINITY

        if opponent_pieces == 0 and opponent_kings == 0:
            return INFINITY

        # Calculate my average score of strategic positions
        if my_pieces == 0:
            my_pieces = 0.00001
        avg_my_pos = my_pos_sum / my_pieces

        # Calculate opponent's average score of strategic positions
        if opponent_pieces == 0:
            opponent_pieces = 0.00001
        avg_opponent_pos = opponent_pos_sum / opponent_pieces

        # Calculate diff between strategic positions score
        avg_pos_diff = avg_my_pos - avg_opponent_pos

        if my_kings > 0:    # I have a king!!!
            # Normalize the distance factor of my kings distance from opponent's pieces
            my_total_king_dist = my_total_king_dist / piece_counts[KING_COLOR[self.color]]
            my_total_king_dist = my_total_king_dist / BOARD_ROWS

            # If I have more kings than the opponent, the distance utility should be lower as the distance grows, so
            # the player will try to minimize it (And get it's kings closer to the opponent's pieces)
            # If the opponent has more kings, the distance utility will be higher as the distance grows, so the player
            # will try to maximize it (And avoid contact from opponent's pieces)
            if king_difference >= 0:
                my_total_king_dist = 1 - my_total_king_dist

        # Create weights for each type of utility factor
        features = [piece_difference, king_difference, avg_pos_diff, my_total_king_dist]
        weights = [100, 50, 1, 1]  # tried different weights but it doesn't make a difference.

        board_utility = 0

        # Calculate total utility based on the weight given to each factor
        for f in range(len(features)):
            fw = features[f] * weights[f]
            board_utility += fw

        return board_utility

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'improved_better_h')

    """
    This method is used for calculating a distance factor of a certain board location from a list of other boards
    locations. The method is used for calculating the distance factor of a king (origLoc) to a list of opponent's
    pieces (destLocs)
    """
    def calculate_distance(self, origLoc, destLocs):
        totalDist = 0
        for destLoc in destLocs:    # Iterate through all other locations
            totalDist += max(abs(origLoc[0] - destLoc[0]), abs(origLoc[1] - destLoc[1])) ** 2

        if (totalDist > 0): # Normalize distance
            totalDist = math.sqrt(totalDist)

        return totalDist

    """
    This method is used to evaluate the scores of locations of board, while giving a higher score for strategic
    locations, thus encouraging the player to occupy and hold those locations. The logic is as follow:
    - A standard location gets a score of 3
    - A location that is on one of the sides of the board get a bit higher score (3.5), those location are strategically
        better since the pawn cannot be threatened in these location
    - A location at the first row or last row gets a higher score (5) - Occupying these lcoations result in either
        preventing the opponent from having a king, or moving my pawns to be kings
    - In case the opponent has less than 2 pawns, the logic is changed, since this is an advanced stage of the game with
        a few pieces on board. In that case there is use for keep holding the above strategic positions, and it is better
        to move my pawns forward and change them to kings. Therefore, the pawn location gets a higher score as it advances
    - A king gets a high score of 5 regardless of its location
    """
    def evaluate_position(self, x , y, is_king, opponent_pawn_count,color):
        if (is_king == True):
            return 5    # Current piece is a king, return 5 regardless of position
        if (opponent_pawn_count < 2):
            #  opponent has no more than 2 pawns, there is no use in holding the board edges, my pawns should move
            #  forward and become kings. Give higher score as pawn advances forward
            return abs(7-BACK_ROW[color]-y)
        if (y == 0 or y == 7):
            return 5    # Current location is back or front row, get a high strategic score
        elif (x == 0 or x == 7):
            return 3.5  # Current location is at the edge of the board, get a medium strategic score
        else:   # Current location is not strategic, get standard score
            return 3

    """
    This method returns the next move of the player by using a minmax search with pruning. The method uses a smart
    time allocation mechanism. The method performs a minmax search layer by layer, but in case the alpha value and
    next move have not changed in 3 layer cycles (Starting from 5 layer), the method stops the search and returns the
    best move so far, thus saving time for future moves.
    When the last move of the cycle is played the method exausts all the remaining time
    """
    def get_move(self, game_state, possible_moves):
        self.clock = time.process_time()
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05

        if len(possible_moves) == 1:
            if self.turns_remaining_in_round == 1:  # This was the last turn in current round
                self.turns_remaining_in_round = self.k  # Reset turns count
                self.time_remaining_in_round = self.time_per_k_turns  # Reset time count
            else:
                self.turns_remaining_in_round -= 1  # Decrease turn amount by 1
                self.time_remaining_in_round -= (time.process_time() - self.clock)  # Update remaining time
            return possible_moves[0]

        current_depth = 1
        prev_alpha = -INFINITY

        # Choosing an arbitrary move in case Minimax does not return an answer:
        best_move = possible_moves[0]

        # Initialize Minimax algorithm, still not running anything
        minimax = MiniMaxWithAlphaBetaPruning(self.utility, self.color, self.no_more_time,
                                              self.selective_deepening_criterion)

        roundsNotChanged = 0
        # Iterative deepening until the time runs out.
        while True:
            print('going to depth: {}, remaining time: {}, prev_alpha: {}, best_move: {}'.format(
                current_depth,
                self.time_for_current_move - (time.process_time() - self.clock),
                prev_alpha,
                best_move))

            try:
                (alpha, move), run_time = run_with_limited_time(
                    minimax.search, (game_state, current_depth, -INFINITY, INFINITY, True), {},
                    self.time_for_current_move - (time.process_time() - self.clock))
            except (ExceededTimeError, MemoryError):
                print('no more time, achieved depth {}'.format(current_depth))
                break

            if self.no_more_time():
                print('no more time')
                break

            # Check if alpha has not changed and next move has not changed
            if (prev_alpha == alpha) and (move.origin_loc == best_move.origin_loc) \
                    and (move.target_loc == best_move.target_loc) and (current_depth > MIN_DEEPENING_DEPTH):
                roundsNotChanged += 1   # alpha and move were not changes - Increment counter
            else:
                roundsNotChanged = 0    # alpha or move were changed - Reset counter

            # alpha and best move have not changed in 3 cycles, stop searching for new moves and sace time for future moves
            if (roundsNotChanged == 3) and (self.turns_remaining_in_round > 1):
                print('Best move and alpha has not changed for {} rounds, depth is {}.'.format(roundsNotChanged, current_depth))
                break

            prev_alpha = alpha
            best_move = move

            if alpha == INFINITY:
                print('the move: {} will guarantee victory.'.format(best_move))
                break

            if alpha == -INFINITY:
                print('all is lost')
                break

            current_depth += 1

        if self.turns_remaining_in_round == 1:  # This was the last turn in current round
            self.turns_remaining_in_round = self.k  # Reset turns count
            self.time_remaining_in_round = self.time_per_k_turns  # Reset time count
        else:
            self.turns_remaining_in_round -= 1  # Decrease turn amount by 1
            self.time_remaining_in_round -= (time.process_time() - self.clock)  # Update remaining time
        return best_move

    """
    This method is used for selective deepening during the minmax search algorithm. In case the next move is a capture,
    this is a move that worths further investigation, thus the method forces the algorithm to keep searching even if 
    the depth limit was reached
    """
    def selective_deepening_criterion(self, state):
        # Get all capture moves available in current state
        possible_capture_moves = state.calc_capture_moves()
        if possible_capture_moves:
            return True # Next move is a capture - Go to a deeper level

        return False
