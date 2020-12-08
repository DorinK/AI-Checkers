
#==============================================================================
# Game pieces
# - RP\BP are pawn pieces
# - RK\BK are king pieces
# - EM is an empty location on the board.
#==============================================================================
RP = 'r'
RK = 'R'
BP = 'b'
BK = 'B'
EM = ' '

RED_PLAYER = 'red'
BLACK_PLAYER = 'black'
TIE = 'tie'

#===============================================================================
# Board Shape
#===============================================================================
BOARD_ROWS = BOARD_COLS = 8

IS_BLACK_TILE = lambda loc: (loc[0] + loc[1]) % 2 == 0

# Assigning colors per tool and player type
PAWN_COLOR = {
    RED_PLAYER: RP,
    BLACK_PLAYER: BP,
}
KING_COLOR = {
    RED_PLAYER: RK,
    BLACK_PLAYER: BK,
}
MY_COLORS = {
    RED_PLAYER: (RP, RK),
    BLACK_PLAYER: (BP, BK)
}
OPPONENT_COLORS = {
    RED_PLAYER: (BP, BK),
    BLACK_PLAYER: (RP, RK),
}

# The ID of the "back" row for each player.
BACK_ROW = {
    RED_PLAYER: BOARD_ROWS - 1,
    BLACK_PLAYER: 0
}

# The Opponent of each Player
OPPONENT_COLOR = {
    RED_PLAYER: BLACK_PLAYER,
    BLACK_PLAYER: RED_PLAYER
}

# Max turns since last Jump
MAX_TURNS_NO_JUMP = 50
