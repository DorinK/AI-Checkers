"""A game-specific implementations of utility functions.
"""
from __future__ import print_function, division
from .consts import *
from .moves import *


class GameState:
    def __init__(self):
        """ Initializing the board and current player.
        """
        self.board = {(i,j) : EM 
                      for j in range(BOARD_COLS) 
                      for i in range(BOARD_ROWS)}
        
        for i in range(3):
            for j in range(BOARD_COLS):
                if IS_BLACK_TILE((i,j)):
                    self.board[(i,j)] = RP
        
        for i in range(3):
            cur_i = BOARD_ROWS - i - 1
            for j in range(BOARD_COLS):
                if IS_BLACK_TILE((cur_i,j)):
                    self.board[(cur_i,j)] = BP
                    
        self.curr_player = RED_PLAYER
        self.turns_since_last_jump = 0

    def calc_single_moves(self):
        """Calculating all the possible single moves.
        :return: All the legitimate single moves for this game state.
        """
        single_pawn_moves = [GameMove(self.board[i], i, j) 
                             for (i, js) in PAWN_SINGLE_MOVES[self.curr_player].items()
                             if self.board[i] == PAWN_COLOR[self.curr_player]
                             for j in js
                             if self.board[j] == EM]
        single_king_moves = [GameMove(self.board[i], i, j)
                             for (i, js) in KING_SINGLE_MOVES.items()
                             if self.board[i] == KING_COLOR[self.curr_player]
                             for j in js
                             if self.board[j] == EM]
        return single_pawn_moves + single_king_moves

    def calc_capture_moves(self):
        """Calculating all the possible capture moves, but only the first step.
        :return: All the legitimate single capture moves for this game state.
        """
        capture_pawn_moves = [(i, j, k)
                              for i, i_capts in PAWN_CAPTURE_MOVES[self.curr_player].items()
                              if self.board[i] == PAWN_COLOR[self.curr_player]
                              for j,k in i_capts
                              if self.board[j] in OPPONENT_COLORS[self.curr_player]
                              and self.board[k] == EM]
        capture_king_moves = [(i, j, k)
                              for i, i_capts in KING_CAPTURE_MOVES.items()
                              if self.board[i] == KING_COLOR[self.curr_player]
                              for j,k in i_capts
                              if self.board[j] in OPPONENT_COLORS[self.curr_player]
                              and self.board[k] == EM]
        return capture_pawn_moves + capture_king_moves
    
    def find_all_capture_sequence(self, origin_loc, cur_loc, possible_moves, already_jumped):
        """
        Calculating all possible capture sequences from cur_loc, using moves in
        possible_moves, avoiding jumping locations in already_jumped
        
        Arguments:
        cur_loc: 2-tuple containing origin location for jump sequence
        possible_moves: all jump moves allowed for player whos sequences we are calculating
        already_jumped: list of 2-tuples of locations of players previously eaten in current sequence
        
        :return: list of 2-tuples where:
            [0] Sequence final location
            [1] list of jumped tools by this sequence
        """
        possible_next_jumps = [(jumped, next_loc)
                               for jumped, next_loc in possible_moves[cur_loc]
                               if self.board[jumped] in OPPONENT_COLORS[self.curr_player] # Jumping opponent tool
                               and (self.board[next_loc] == EM or next_loc == origin_loc)# Target location is empty
                               and jumped not in already_jumped] # I have not jumped this tool yet in this sequence
        
        capture_seqs = []
        for jumped, next_loc in possible_next_jumps:
            cur_seqs = self.find_all_capture_sequence(origin_loc,
                                                      next_loc, 
                                                      possible_moves,
                                                      already_jumped + [jumped])
            for target, seq in cur_seqs:
                capture_seqs.append((target, [jumped] + seq))
        
        if len(capture_seqs) == 0:
            return [(cur_loc,[])]
        else:
            return capture_seqs
    
    def get_possible_moves(self):
        """Return a list of possible moves for this state.
        Each possible move is represented by GameMove object.
        """
        possible_capture_moves = self.calc_capture_moves()
        if possible_capture_moves:
            capture_origins = set(origin for origin,_,_ in possible_capture_moves)
            capture_seqs = []
            for origin in capture_origins:
                cur_seqs = self.find_all_capture_sequence(origin, origin,
                                                          TOOL_CAPTURE_MOVES[self.board[origin]], 
                                                          [])
                for target, seq in cur_seqs:
                    capture_seqs.append(GameMove(self.board[origin], origin, target, seq))
                    
            return capture_seqs

        # There were no capture moves. We return the single moves.
        return self.calc_single_moves()

    def perform_move(self, move):
        self.board[move.origin_loc] = EM
        if (move.player_type == PAWN_COLOR[self.curr_player]
            and move.target_loc[0] == BACK_ROW[self.curr_player]):
            # If moved pawn to back row, turn to king and put in target
            self.board[move.target_loc] = KING_COLOR[self.curr_player]
        else:
            # Move tool to target
            self.board[move.target_loc] = move.player_type
        
        for loc in move.jumped_locs:
            self.board[loc] = EM
        if len(move.jumped_locs) > 0:
            self.turns_since_last_jump = 0
        else:
            self.turns_since_last_jump += 0.5        
        
        # Updating the current player.
        self.curr_player = OPPONENT_COLOR[self.curr_player]
        
    def draw_board(self):
        print("  " + " ".join([str(i) for i in range(BOARD_COLS)]))
        line_sep = " +" + "-+"*BOARD_COLS
        print(line_sep)
        for i in range(BOARD_ROWS):
            print(str(i) + "|" + "|".join([self.board[(i,j)]
                                           for j in range(BOARD_COLS)]) + "|")
            print(line_sep)
        print("\n" + self.curr_player + " Player Turn!\n\n")

    def __hash__(self):
        """This object can be inserted into a set or as dict key. NOTICE: Changing the object after it has been inserted
        into a set or dict (as key) may have unpredicted results!!!
        """
        return hash(','.join([self.board[(i,j)]
                              for i in range(BOARD_ROWS)
                              for j in range(BOARD_COLS)] + [self.curr_player]))

    def __eq__(self, other):
        return isinstance(other, GameState) and self.board == other.board and self.curr_player == other.curr_player

