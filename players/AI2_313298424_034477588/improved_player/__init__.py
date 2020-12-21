# ===============================================================================
# Imports
# ===============================================================================

import time
import abstract
from players import simple_player
from utils import MiniMaxWithAlphaBetaPruning, INFINITY, run_with_limited_time, ExceededTimeError

# ===============================================================================
# Globals
# ===============================================================================

MIN_DEEPENING_DEPTH = 5


# ===============================================================================
# Player
# ===============================================================================


class Player(simple_player.Player):

    """
    This class implements the improved player.
    This player has a smart time management mechanism in order to divide the time allocated to K turns wisely between
    all K turns.
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

    def selective_deepening_criterion(self, state):

        """
        This method is used for selective deepening during the minimax search algorithm. In case the next move is a
        capture, this is a move that worths further investigation, thus we force the algorithm to keep searching even if
        the depth limit was reached.
        """

        # Get all capture moves available in current state.
        possible_capture_moves = state.calc_capture_moves()

        # If next move is a capture - Go to a deeper level.
        if possible_capture_moves:
            return True

        return False

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'improved')
