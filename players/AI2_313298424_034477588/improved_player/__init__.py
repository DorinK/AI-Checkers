import abstract
from players import simple_player
from utils import MiniMaxWithAlphaBetaPruning, INFINITY, run_with_limited_time, ExceededTimeError
from checkers.consts import EM, PAWN_COLOR, KING_COLOR, OPPONENT_COLOR, BACK_ROW, BOARD_ROWS, RED_PLAYER, BLACK_PLAYER, BOARD_COLS
import time
from collections import defaultdict


MIN_DEEPENING_DEPTH = 5


class Player(simple_player.Player):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        simple_player.Player.__init__(self, setup_time, player_color, time_per_k_turns, k)

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
        possible_capture_moves = state.calc_capture_moves()
        if possible_capture_moves:
            return True # Next move is a capture - Go to a deeper level

        return False

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'improved')