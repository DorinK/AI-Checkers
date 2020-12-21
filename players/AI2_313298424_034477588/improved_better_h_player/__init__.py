# ===============================================================================
# Imports
# ===============================================================================

import math
import time
import abstract
from collections import defaultdict
from checkers.consts import EM, PAWN_COLOR, KING_COLOR, OPPONENT_COLOR, MAX_TURNS_NO_JUMP, MY_COLORS, BACK_ROW, BOARD_ROWS
from players import simple_player
from utils import MiniMaxWithAlphaBetaPruning, INFINITY, run_with_limited_time, ExceededTimeError

# ===============================================================================
# Globals
# ===============================================================================

PAWN_WEIGHT = 1
KING_WEIGHT = 1.5
MIN_DEEPENING_DEPTH = 5


# ===============================================================================
# Player
# ===============================================================================


class Player(simple_player.Player):

    """
    This class implements the improved_better_h player.
    This player has both an advanced utility calculation, a time management logic that saves time for future moves and a
    selective deepening criterion that forces the minimax algorithm to deepen the search in case the next move is a
    capture, even if the depth limit was already reached.
    """

    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        simple_player.Player.__init__(self, setup_time, player_color, time_per_k_turns, k)

    def get_move(self, game_state, possible_moves):

        """
        This method returns the next move of the player by using a minimax search with Alpha-Beta pruning. In this
        method we apply a smart time management mechanism. The method performs a minimax search layer by layer, but in
        case the alpha value and best next move have not been changed in 3 layer cycles (Starting from 5 layer) we stop
        the search and the best move so far is returned, thus saving time for future moves.
        In the last turn of the cycle, we exhaust all the remaining time.
        """

        self.clock = time.process_time()
        self.time_for_current_move = self.time_remaining_in_round / self.turns_remaining_in_round - 0.05

        # If there is only one possible move.
        if len(possible_moves) == 1:

            # If this was the last turn in current round.
            if self.turns_remaining_in_round == 1:
                self.turns_remaining_in_round = self.k  # Reset turns count.
                self.time_remaining_in_round = self.time_per_k_turns  # Reset time count.

            else:
                self.turns_remaining_in_round -= 1  # Decrease turns amount by 1.
                self.time_remaining_in_round -= (time.process_time() - self.clock)  # Update remaining time.

            return possible_moves[0]

        current_depth = 1
        prev_alpha = -INFINITY

        # Choosing an arbitrary move in case Minimax does not return an answer.
        best_move = possible_moves[0]

        # Initialize Minimax algorithm, still not running anything.
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

            # Check if both alpha and next best move according to the last search has not been changed.
            if prev_alpha == alpha and move.origin_loc == best_move.origin_loc \
                    and move.target_loc == best_move.target_loc and current_depth > MIN_DEEPENING_DEPTH:

                # If so, then increment the counter.
                roundsNotChanged += 1

            else:  # alpha or next best move were changed - Reset counter.
                roundsNotChanged = 0

            # If alpha and best move have not been changed in 3 cycles, stop searching and save time for future moves.
            if roundsNotChanged == 3 and self.turns_remaining_in_round > 1:
                print('Best move and alpha has not changed for {} rounds, depth is {}.'.format(roundsNotChanged,
                                                                                               current_depth))
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

        # If this was the last turn in current round.
        if self.turns_remaining_in_round == 1:
            self.turns_remaining_in_round = self.k  # Reset turns count.
            self.time_remaining_in_round = self.time_per_k_turns  # Reset time count.
        else:
            self.turns_remaining_in_round -= 1  # Decrease turns amount by 1.
            self.time_remaining_in_round -= (time.process_time() - self.clock)  # Update remaining time.

        return best_move

    def utility(self, state):

        """
        This method implements the utility calculation of the better_h player. The utility function takes into account 4
        types of factors:
         1. The difference in amount of pieces of both players.
         2. The difference in amount of kings of both players.
         3. The difference in score that is calculated for each player's pieces based on their position, while boosting
            strategic positions (See explanation in evaluate_position function).
         4. A score based on the distance between the player's kings and the opponent's pieces. This score is used for
            either moving the player's kings closer to the opponent's pieces in case the player has kings advantage, or
            moving the player's kings away from opponent's pieces in case the opponent has kings advantage.
        """

        # If there is no possible moves.
        if len(state.get_possible_moves()) == 0:
            return INFINITY if state.curr_player != self.color else -INFINITY

        if state.turns_since_last_jump >= MAX_TURNS_NO_JUMP:
            return 0

        # A dictionary that will hold the counts of each type of piece.
        piece_counts = defaultdict(lambda: 0)

        # A dictionary that will hold the list of positions of each type of piece.
        piece_locs = defaultdict(lambda: [])

        for loc, loc_val in state.board.items():

            # If current location is not empty.
            if loc_val != EM:
                piece_counts[loc_val] += 1  # Increment amount of current piece type.
                piece_locs[loc_val].append(loc)  # Add the location of current piece.

        # Get opponent's color.
        opponent_color = OPPONENT_COLOR[self.color]

        opponent_pos_sum = 0
        my_pos_sum = 0
        my_total_king_dist = 0

        # Count amount of pieces and amount of kings - ours and the opponent's.
        my_pieces = piece_counts[PAWN_COLOR[self.color]] + piece_counts[KING_COLOR[self.color]]
        opponent_pieces = piece_counts[PAWN_COLOR[opponent_color]] + piece_counts[KING_COLOR[opponent_color]]
        my_kings = piece_counts[KING_COLOR[self.color]]
        opponent_kings = piece_counts[KING_COLOR[opponent_color]]

        # Iterate through all locations on the board.
        for loc, loc_val in state.board.items():

            # If current location is not empty.
            if loc_val != EM:

                # And if this location contains our color.
                if loc_val in MY_COLORS[self.color]:

                    # Get score of current location - Give boost to strategic locations.
                    my_pos = self.evaluate_position(loc[1], loc[0], loc_val == KING_COLOR[self.color],
                                                    piece_counts[PAWN_COLOR[opponent_color]], self.color)
                    # Sum positions score.
                    my_pos_sum += my_pos

                    # If current piece is a king.
                    if loc_val == KING_COLOR[self.color]:

                        # Calculate distances factor of all kings from all of opponent's pieces.
                        dist = self.calculate_distance(loc, piece_locs[KING_COLOR[opponent_color]])
                        dist += self.calculate_distance(loc, piece_locs[PAWN_COLOR[opponent_color]])
                        my_total_king_dist += dist

                else:  # This location contains the opponent's color.

                    # Get score of current location - Give boost to strategic locations.
                    opponent_pos = self.evaluate_position(loc[1], loc[0], loc_val == KING_COLOR[opponent_color],
                                                          piece_counts[PAWN_COLOR[self.color]], opponent_color)
                    # Sum opponent's positions score.
                    opponent_pos_sum += opponent_pos

        # Calculate total pieces difference and total kings difference.
        piece_difference = my_pieces - opponent_pieces
        king_difference = my_kings - opponent_kings

        # If we have no tools left.
        if my_pieces == 0 and my_kings == 0:
            return -INFINITY

        # If the opponent has no tools left.
        if opponent_pieces == 0 and opponent_kings == 0:
            return INFINITY

        # Calculate our average score of strategic positions.
        if my_pieces == 0:
            my_pieces = 0.00001
        avg_my_pos = my_pos_sum / my_pieces

        # Calculate opponent's average score of strategic positions.
        if opponent_pieces == 0:
            opponent_pieces = 0.00001
        avg_opponent_pos = opponent_pos_sum / opponent_pieces

        # Calculate diff between strategic positions score.
        avg_pos_diff = avg_my_pos - avg_opponent_pos

        # If we have a king.
        if my_kings > 0:

            # Normalize the distance factor of our kings from opponent's pieces.
            my_total_king_dist = my_total_king_dist / piece_counts[KING_COLOR[self.color]]
            my_total_king_dist = my_total_king_dist / BOARD_ROWS

            # If we have more kings than the opponent, the distance score should be lower as the distance grows, so
            # the player will try to minimize it (And get it's kings closer to the opponent's pieces).
            # If the opponent has more kings, the distance score will be higher as the distance grows, so the player
            # will try to maximize it (And avoid contact with opponent's pieces).
            if king_difference >= 0:
                my_total_king_dist = 1 - my_total_king_dist

        # Defining weights for each type of utility factor.
        features = [piece_difference, king_difference, avg_pos_diff, my_total_king_dist]
        weights = [100, 50, 1, 1]

        board_utility = 0

        # Calculate total utility based on the weight given to each factor.
        for f in range(len(features)):
            fw = features[f] * weights[f]
            board_utility += fw

        return board_utility

    def calculate_distance(self, origLoc, destLocs):

        """
        This method is used for calculating a distance factor of a certain board location from a list of other board
        locations. That is, calculating the distance factor of a king (origLoc) from a list of opponent's pieces
        (destLocs).
        """

        totalDist = 0

        # Iterate over all other locations.
        for destLoc in destLocs:
            totalDist += max(abs(origLoc[0] - destLoc[0]), abs(origLoc[1] - destLoc[1])) ** 2

        if totalDist > 0:  # Normalize distance.
            totalDist = math.sqrt(totalDist)

        return totalDist

    def evaluate_position(self, x, y, is_king, opponent_pawn_count, color):

        """
        This method is used to evaluate the scores of locations on the board, while giving a higher score for strategic
        locations, thus encouraging the player to occupy and hold those locations. The logic is as follows:
        - A standard location gets a score of 3.
        - A location that is on one of the sides of the board gets a bit higher score (3.5). Those location are
          strategically better since the pawn cannot be threatened there.
        - A location at the first row or last row gets a higher score (5) - Occupying these locations results in either
          preventing the opponent from having a king, or moving our pawns to be kings.
        - In case the opponent has been left with less than 2 pawns, the logic is being changed, since this is an
          advanced stage of the game with a few pieces on the board. In that case, there is no point for keep in
          continuing to hold the above strategic positions, and it is better to move our pawns forward and make them
          kings. Therefore, the pawn location gets a higher score as it advances.
        - A king gets a high score of 5 regardless of its location, since having a king is an advantage.
        """

        # If current piece is a king, return 5 regardless of it's position.
        if is_king:
            return 5

        #  If opponent has no more than 2 pawns, there is no point in holding the board edges, our pawns should move
        #  forward and become kings. Give higher score as pawn advances forward.
        if opponent_pawn_count < 2:
            return abs(7 - BACK_ROW[color] - y)

        # If current location is back or front row, get a high strategic score.
        if y == 0 or y == 7:
            return 5

        # If current location is at the edge of the board, get a medium strategic score.
        elif x == 0 or x == 7:
            return 3.5

        else:  # Current location is not strategic, get standard score.
            return 3

    def selective_deepening_criterion(self, state):

        """
        This method is used for selective deepening during the minimax search algorithm. In case the next move is a
        capture, this is a move that worths further investigation, thus we force the algorithm to keep searching even if
        the depth limit was already reached.
        """

        # Get all capture moves available in current state.
        possible_capture_moves = state.calc_capture_moves()

        # If next move is a capture - Go to a deeper level.
        if possible_capture_moves:
            return True

        return False

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'improved_better_h')
