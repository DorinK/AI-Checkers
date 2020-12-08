"""
This file holds all objects relating to the moves possible in the game.
"""

#===============================================================================
# Imports
#===============================================================================

from .consts import (RED_PLAYER, BLACK_PLAYER, 
                     BOARD_ROWS, BOARD_COLS, 
                     IS_BLACK_TILE, 
                     RP, RK, BP, BK)

#===============================================================================
# Classes
#===============================================================================

class GameMove:
    def __init__(self, player_type, origin_loc, target_loc, jumped_locs = None):
        """
        :param: player_type of the tool moved, could be RP, RK, BP, BK
        :param: origin_loc a 2-tuple defining the location on the board of the tool
        :param: target_loc a 2-tuple defining the location on the board we would like
            to move the tool to. In multiple jumps this is the final destination.
        :param: jumped_locs is a list of tools we jumped during our move. If this
            is None or an empty list, this is an ordinary move and not a jump
        """
        self.player_type = player_type
        self.origin_loc = origin_loc
        self.target_loc = target_loc
        self.jumped_locs = jumped_locs if jumped_locs is not None else []
        
    def __str__(self):
        s = " ".join(["Move", self.player_type,
                      "from", str(self.origin_loc),
                      "to", str(self.target_loc)])
        if len(self.jumped_locs) > 0:
            s += ", eat: " + ",".join([str(loc) for loc in self.jumped_locs])
        
        return s
        
#===============================================================================
# Move Constants
#===============================================================================

# Directions:
# Down: row += 1
# Up: row -= 1
# Right: col += 1
# Left: col -= 1

# Generating the possible single moves.

# The following Dicts are of the form 2-tuple:2-tuple, where the key is the tool 
# location and the value is the location it can go in an ordinary move in that direction
DOWN_RIGHT_SINGLE_MOVES = {(i,j) : (i+1, j+1) 
                           for i in range(BOARD_ROWS - 1) 
                           for j in range(BOARD_COLS - 1)
                           if IS_BLACK_TILE((i,j))}
DOWN_LEFT_SINGLE_MOVES = {(i,j) : (i+1, j-1) 
                          for i in range(BOARD_ROWS - 1) 
                          for j in range(1, BOARD_COLS)
                          if IS_BLACK_TILE((i,j))}
UP_RIGHT_SINGLE_MOVES = {(i,j) : (i-1, j+1) 
                         for i in range(1, BOARD_ROWS) 
                         for j in range(BOARD_COLS - 1)
                         if IS_BLACK_TILE((i,j))}
UP_LEFT_SINGLE_MOVES = {(i,j) : (i-1, j-1)
                         for i in range(1, BOARD_ROWS) 
                         for j in range(1, BOARD_COLS)
                         if IS_BLACK_TILE((i,j))}

# The following Dicts are of the form 2-tuple:list of 2-tuples, where the key is the
# tool location and the value is a list of locations it can go to in an ordinary move
# in the specified direction. KING_SINGLE_MOVES holds all moves to all directions for
# a king in the key position.
UP_SINGLE_MOVES = {(i,j) : list(filter(None,[UP_RIGHT_SINGLE_MOVES.get((i,j),None),UP_LEFT_SINGLE_MOVES.get((i,j),None)]))
                   for i in range(BOARD_ROWS)
                   for j in range(BOARD_COLS)
                   if IS_BLACK_TILE((i,j))}
DOWN_SINGLE_MOVES = {(i,j) : list(filter(None,[DOWN_RIGHT_SINGLE_MOVES.get((i,j),None),DOWN_LEFT_SINGLE_MOVES.get((i,j),None)]))
                     for i in range(BOARD_ROWS)
                     for j in range(BOARD_COLS)
                     if IS_BLACK_TILE((i,j))}
KING_SINGLE_MOVES = {(i,j) : UP_SINGLE_MOVES[(i,j)] + DOWN_SINGLE_MOVES[(i,j)]
                     for i in range(BOARD_ROWS)
                     for j in range(BOARD_COLS)
                     if IS_BLACK_TILE((i,j))}

# Capture moves are just two single moves of the same type
def calc_capture_moves(single_moves):
    return {i : (j, single_moves[j])
            for i,j in single_moves.items()
            if j in single_moves}

# The following Dicts are of the form 2-tuple:2-tuple of 2-tuples, where the key is the tool 
# location and the value describes a possible jump from that location in that direction.
# The jumps are a 2-tuple of the jumped location(enemy tool) and the final location.
DOWN_RIGHT_CAPTURE_MOVES = calc_capture_moves(DOWN_RIGHT_SINGLE_MOVES)
DOWN_LEFT_CAPTURE_MOVES = calc_capture_moves(DOWN_LEFT_SINGLE_MOVES)
UP_RIGHT_CAPTURE_MOVES = calc_capture_moves(UP_RIGHT_SINGLE_MOVES)
UP_LEFT_CAPTURE_MOVES = calc_capture_moves(UP_LEFT_SINGLE_MOVES)

# The following Dicts are of the form 2-tuple:list of 2-tuples of 2-tuples, where the
# key is the tool location and the value is a list of possible jumps from that location
# in the specified direction. KING_CAPTURE_MOVES holds jumps in all possible directions
# from the current direction.
UP_CAPTURE_MOVES = {(i,j) : list(filter(None,[UP_RIGHT_CAPTURE_MOVES.get((i,j),None), UP_LEFT_CAPTURE_MOVES.get((i,j),None)]))
                    for i in range(BOARD_ROWS)
                    for j in range(BOARD_COLS)
                    if IS_BLACK_TILE((i,j))}
DOWN_CAPTURE_MOVES = {(i,j) : list(filter(None, [DOWN_RIGHT_CAPTURE_MOVES.get((i,j),None), DOWN_LEFT_CAPTURE_MOVES.get((i,j),None)]))
                      for i in range(BOARD_ROWS)
                      for j in range(BOARD_COLS)
                      if IS_BLACK_TILE((i,j))}
KING_CAPTURE_MOVES = {(i,j) : UP_CAPTURE_MOVES[(i,j)] + DOWN_CAPTURE_MOVES[(i,j)]
                      for i in range(BOARD_ROWS)
                      for j in range(BOARD_COLS)
                      if IS_BLACK_TILE((i,j))}

# Dictionaries assigning possible moves to specific players by color.
PAWN_SINGLE_MOVES = {
    RED_PLAYER: DOWN_SINGLE_MOVES,
    BLACK_PLAYER: UP_SINGLE_MOVES,
}

PAWN_CAPTURE_MOVES = {
    RED_PLAYER: DOWN_CAPTURE_MOVES,
    BLACK_PLAYER: UP_CAPTURE_MOVES,
}

TOOL_CAPTURE_MOVES = {
    RP : DOWN_CAPTURE_MOVES,
    RK: KING_CAPTURE_MOVES,
    BP : UP_CAPTURE_MOVES,
    BK : KING_CAPTURE_MOVES,
}
