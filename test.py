# ===============================================================================
# Important Notes (!)
# ===============================================================================
"""
    1. After every match we test, we delete the EXCEL file and rewrite everything
    with the additional data.

    2. Run DemoTest before Test - the main test might take a few hours so make sure
    there are not runtime errors you didn't notice.

    3. DON'T OPEN THE EXCEL FILE BEFORE PROGRAM ENDS. if you do, it might crash
    the program and you'll have to start all over.
"""

# ===============================================================================
# Imports
# ===============================================================================

import csv
import sys
import os
import run_game
from typing import List
from run_game import TIE
from checkers.consts import BLACK_PLAYER, RED_PLAYER

# ===============================================================================
# Globals
# ===============================================================================

LOSE_SCORE = 0
TIE_SCORE = 0.5
WIN_SCORE = 1
TEST_COUNT = 1

# Redirect output from game match to focus on results of each match
CONSOLE_STREAM = sys.stdout
sys.stdout = open(os.devnull, 'w')


def Test(times: List[str], players_names: List[str], result_file_name: str):

    global TEST_COUNT
    print(f'Starting test #{TEST_COUNT}', file=CONSOLE_STREAM)
    TEST_COUNT += 1

    # Args for runne:
    # 0: setup_time, 1: round_time, 2: k, 3: verbose, 4: Player1, 5: Player2
    args = ['2', '', '5', 'n', '', '']

    # Create each match.
    dous = []
    for i in range(len(players_names) - 1):
        for j in range(i + 1, len(players_names)):
            dous.append((players_names[i], players_names[j]))  # P1 vs P2
            dous.append((players_names[j], players_names[i]))  # P2 vs P1

    # Store all results to update file on the run.
    results = [['TEST START']]

    # Iterate times per round
    for t in times:
        args[1] = t

        for player1, player2 in dous:

            # FIRST GAME: player 1 starts
            args[4], args[5] = player1, player2
            runner = run_game.GameRunner(*args)
            winner = runner.run()

            match_result = [player1.split('.')[1], player2.split('.')[1], t]

            if winner == TIE:
                match_result.extend([TIE_SCORE, TIE_SCORE])

            elif winner[0] == RED_PLAYER:
                match_result.extend([WIN_SCORE, LOSE_SCORE])

            else:
                match_result.extend([LOSE_SCORE, WIN_SCORE])
            results.append(match_result)

            print(f'current result: {match_result}', file=CONSOLE_STREAM)

            with open(result_file_name+'.csv', 'w', newline='') as file:
                writer = csv.writer(file, delimiter=',')
                for row, result in enumerate(results[1:]):
                    writer.writerow(result)


# Quickly run all tests to see there aren't any runtime errors.
def DemoTest():
    demo_times = ['1']
    demo_players = ['AI2_313298424_034477588.simple_player', 'AI2_313298424_034477588.improved_better_h_player',
                    'AI2_313298424_034477588.better_h_player', 'AI2_313298424_034477588.improved_player']
    demo_result_file = 'demo_results'
    Test(demo_times, demo_players, demo_result_file)


if __name__ == '__main__':
    T = ['2', '10', '50']
    result_file = 'experiments'
    players = ['AI2_313298424_034477588.simple_player', 'AI2_313298424_034477588.improved_better_h_player',
               'AI2_313298424_034477588.better_h_player', 'AI2_313298424_034477588.improved_player']
    Test(T, players, result_file)
