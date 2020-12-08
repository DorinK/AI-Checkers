"""
A generic turn-based game runner.
"""
import sys
from checkers.board import GameState
from checkers.consts import RED_PLAYER, BLACK_PLAYER, TIE, OPPONENT_COLOR, MAX_TURNS_NO_JUMP
import utils
import copy
import players.interactive

class GameRunner:
    def __init__(self, setup_time, time_per_k_turns, k, verbose, red_player, black_player):
        """Game runner initialization.

        :param setup_time: Setup time allowed for each player in seconds.
        :param time_per_k_turns: Time allowed per k moves in seconds.
            The interactive player always gets infinite time to decide, no matter what.
        :param k: The k turns we measure time on. Must be a positive integer.
        :param verbose: preference of printing the board each turn. 'y' - yes, print. 'n' - no,  don't print.
        :param red_player: The name of the module containing the red player. E.g. "myplayer" will invoke an
            equivalent to "import players.myplayer" in the code.
        :param black_player: Same as 'red_player' parameter, but for the black one.
        """

        self.verbose = verbose.lower()
        self.setup_time = float(setup_time)
        self.time_per_k_turns = float(time_per_k_turns)
        self.k = int(k)
        self.players = {}

        # Dynamically importing the players. This allows maximum flexibility and modularity.
        self.red_player = 'players.{}'.format(red_player)
        self.black_player = 'players.{}'.format(black_player)
        __import__(self.red_player)
        __import__(self.black_player)
        red_is_interactive = sys.modules[self.red_player].Player == players.interactive.Player
        black_is_interactive = sys.modules[self.black_player].Player == players.interactive.Player
        
        self.player_move_times = {
            RED_PLAYER : utils.INFINITY if red_is_interactive else self.time_per_k_turns,
            BLACK_PLAYER: utils.INFINITY if black_is_interactive else self.time_per_k_turns,
        }

    def setup_player(self, player_class, player_color):
        """ An auxiliary function to populate the players list, and measure setup times on the go.

        :param player_class: The player class that should be initialized, measured and put into the list.
        :param player_color: Player color, passed as an argument to the player.
        :return: A boolean. True if the player exceeded the given time. False otherwise.
        """
        try:
            player, measured_time = utils.run_with_limited_time(
                player_class, (self.setup_time, player_color, self.time_per_k_turns, self.k), {}, self.setup_time*1.5)
        except MemoryError:
            return True

        self.players[player_color] = player
        return measured_time > self.setup_time

    def run(self):
        """The main loop.
        :return: The winner.
        """
        # Setup each player 
        red_player_exceeded = self.setup_player(sys.modules[self.red_player].Player, RED_PLAYER)
        black_player_exceeded = self.setup_player(sys.modules[self.black_player].Player, BLACK_PLAYER)
        winner = self.handle_time_expired(red_player_exceeded, black_player_exceeded)
        if winner: # One of the players exceeded the setup time
            return winner

        board_state = GameState()
        remaining_run_times = copy.deepcopy(self.player_move_times)
        k_count = 0

        # Running the actual game loop. The game ends if someone is left out of moves,
        # or exceeds his time.
        while True:
            if self.verbose == 'y':
                board_state.draw_board()

            player = self.players[board_state.curr_player]
            remaining_run_time = remaining_run_times[board_state.curr_player]
            try:
                possible_moves = board_state.get_possible_moves()
                if not possible_moves:
                    winner = self.make_winner_result(OPPONENT_COLOR[board_state.curr_player])
                    break
                # Get move from player
                move, run_time = utils.run_with_limited_time(
                    player.get_move, (copy.deepcopy(board_state), possible_moves), {}, remaining_run_time*1.5) ###
                
                remaining_run_times[board_state.curr_player] -= run_time
                if remaining_run_times[board_state.curr_player] < 0:
                    raise utils.ExceededTimeError
            
            except (utils.ExceededTimeError, MemoryError):
                print('Player {} exceeded resources.'.format(player))
                winner = self.make_winner_result(OPPONENT_COLOR[board_state.curr_player])
                break

            board_state.perform_move(move)
            if self.verbose == 'y':
                print('Player ' + repr(player) + ' performed the move: ' + str(move))
            
            if board_state.turns_since_last_jump >= MAX_TURNS_NO_JUMP:
                print('Number of turns without jumps exceeded {}'.format(MAX_TURNS_NO_JUMP))
                winner = self.make_winner_result(TIE)
                break
            
            if board_state.curr_player == RED_PLAYER:
                # red and black played.
                k_count = (k_count + 1) % self.k
                if k_count == 0:
                    # K rounds completed. Resetting timers.
                    remaining_run_times = copy.deepcopy(self.player_move_times)

        self.end_game(winner)
        return winner

    @staticmethod
    def end_game(winner):
        if winner == TIE:
            print('The game ended in a tie!')
        else:
            print('The winner is {}'.format(winner[1]))

    def make_winner_result(self, winner):
        if winner == TIE:
            return TIE
        else:
            return winner, self.players[winner]

    def handle_time_expired(self, red_player_exceeded, black_player_exceeded):
        winner = None
        if red_player_exceeded and black_player_exceeded:
            winner = self.make_winner_result(TIE)
        elif red_player_exceeded:
            winner = self.make_winner_result(BLACK_PLAYER)
        elif black_player_exceeded:
            winner = self.make_winner_result(RED_PLAYER)

        if winner:
            self.end_game(winner)

        return winner


if __name__ == '__main__':
    try:
        GameRunner(*sys.argv[1:]).run()
    except TypeError:
        print("""Syntax: {0} setup_time time_per_k_turns k verbose red_player black_player
For example: {0} 2 10 5 y interactive random_player
Please read the docs in the code for more info.""".
              format(sys.argv[0]))