
import abstract
from players import simple_player
from utils import MiniMaxWithAlphaBetaPruning, INFINITY, run_with_limited_time, ExceededTimeError
from checkers.consts import EM, PAWN_COLOR, KING_COLOR, OPPONENT_COLOR, BACK_ROW, BOARD_ROWS, RED_PLAYER, BLACK_PLAYER, BOARD_COLS
import time
from collections import defaultdict


MIN_DEEPENING_DEPTH = 4
# The ID of the "back" row for each player.
ROW_BEFORE_BACK_ROW = {
    RED_PLAYER: BOARD_ROWS - 2,
    BLACK_PLAYER: 1
}


class Player(simple_player.Player):
    def __init__(self, setup_time, player_color, time_per_k_turns, k):
        simple_player.Player.__init__(self, setup_time, player_color, time_per_k_turns, k)
        #self.opponent_color = OPPONENT_COLOR[player_color]
        #self.opponent_row_before_back_row = ROW_BEFORE_BACK_ROW[self.opponent_color]


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


            if (prev_alpha == alpha) and (move.origin_loc == best_move.origin_loc) \
                    and (move.target_loc == best_move.target_loc) and (current_depth > MIN_DEEPENING_DEPTH):
                roundsNotChanged += 1
            else:
                roundsNotChanged = 0

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

    def selective_deepening_criterion(self, state):
        possible_capture_moves = state.calc_capture_moves()
        if possible_capture_moves:
            return True # Next move is a capture - Go to a deeper level

        """
        for col in range(BOARD_COLS):
            curLoc = (self.opponent_row_before_back_row, col)   # Iterate through all location of row before back row of opponent
            if state.board[curLoc] == PAWN_COLOR[self.opponent_color]:    # There is an opponent pawn in last row before back row
                next_col = col-1
                if (next_col >= 0) and state.board[(BACK_ROW[self.opponent_color], next_col)] == EM:
                    print(f"Cur loc={curLoc}, pawn={state.board[curLoc]}, next=({BACK_ROW[self.opponent_color]},{next_col}), state={state.board[(BACK_ROW[self.opponent_color], next_col)]}")
                    return True # Next location is empty = Opponent is going to have a king - Go to a deeper level
                next_col = col + 1
                if (next_col < BOARD_COLS) and state.board[(BACK_ROW[self.opponent_color], next_col)] == EM:
                    print(f"Cur loc={curLoc}, pawn={state.board[curLoc]}, next=({BACK_ROW[self.opponent_color]},{next_col}), state={state.board[(BACK_ROW[self.opponent_color], next_col)]}")
                    return True  # Next location is empty = Opponent is going to have a king - Go to a deeper level
        """

        return False

    def __repr__(self):
        return '{} {}'.format(abstract.AbstractPlayer.__repr__(self), 'improved')