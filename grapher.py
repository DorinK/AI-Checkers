from collections import defaultdict
import matplotlib.pyplot as plt
from tabulate import tabulate
import pandas as pd

# ==================
#      Globals
# ==================

SIMPLE_PLAYER = 'simple_player'
IMPROVED_PLAYER = 'improved_player'
BETTER_H_PLAYER = 'better_h_player'
IMPROVED_BETTER_H_PLAYER = 'improved_better_h_player'

PLAYERS = {SIMPLE_PLAYER: defaultdict(list), IMPROVED_PLAYER: defaultdict(list),
           BETTER_H_PLAYER: defaultdict(list), IMPROVED_BETTER_H_PLAYER: defaultdict(list)}

PLAYER_SCORE = {SIMPLE_PLAYER: defaultdict(), IMPROVED_PLAYER: defaultdict(), BETTER_H_PLAYER: defaultdict(),
                IMPROVED_BETTER_H_PLAYER: defaultdict()}

# ==================
#     Preprocess
# ==================

# Read the CSV file.
file_name = 'results.csv'
df = pd.read_csv(file_name, sep=',', header=None)

# Collect the games scores of each player for each time limitation.
for index, row in df.iterrows():
    PLAYERS[row[0]][row[2]].append(row[3])
    PLAYERS[row[1]][row[2]].append(row[4])

# Calculate each player's score in each time limitation.
for player in PLAYERS:
    for time in PLAYERS[player].keys():
        PLAYER_SCORE[player][time] = sum(PLAYERS[player][time])

# ==================
#  Print Scoreboard
# ==================

# Print the table with the scores.
table_data = [[player] + list(PLAYER_SCORE[player].values()) for player in PLAYER_SCORE]
print(tabulate(table_data, headers=["", "t = 2", "t = 10", "t = 50"], tablefmt='fancy_grid',
               colalign=("center", "center", "center", "center")))

# ==================
#   Plot the Graph
# ==================

plt.title('Score as a function of t', pad=14)
plt.xlabel('Time')
plt.ylabel('Score')

ax = plt.gca()
ax.xaxis.set_label_coords(0.485, -0.09)
ax.yaxis.set_label_coords(-0.09, 0.5)

default_colors = plt.rcParams['axes.prop_cycle'].by_key()['color']
colors = [default_colors[4], default_colors[0], 'salmon', 'teal']

for i, player in enumerate(PLAYER_SCORE):

    plt.plot(list(PLAYER_SCORE[player].keys()), list(PLAYER_SCORE[player].values()), label=player, marker='o',
             color=colors[i])

    for idx, (a, b) in enumerate(zip(list(PLAYER_SCORE[player].keys()), list(PLAYER_SCORE[player].values()))):

        if idx == 2:
            y = (b + 0.17) if player not in [IMPROVED_BETTER_H_PLAYER, IMPROVED_PLAYER] else (b - 0.3)
        else:
            y = (b + 0.17) if player != IMPROVED_PLAYER else (b - 0.3)

        ax.text(a, y, str(b), fontsize=6, bbox={'facecolor': colors[i], 'alpha': 0.1, 'pad': 1.5},
                verticalalignment='bottom', horizontalalignment='center')

plt.legend(loc='lower center', bbox_to_anchor=(0.51, -0.35), ncol=2, frameon=False, labelspacing=1, columnspacing=3.5)
plt.subplots_adjust(bottom=0.23)
plt.show()

# for player,color in zip(PLAYER_SCORE,[colors[4],'teal',colors[0],colors[3],]): #'salmon' crimson [default,'teal','orange','indigo'] 2
# for player,color in zip(PLAYER_SCORE,[colors[0],'crimson','teal','indigo',]): #'salmon' crimson [default,'teal','orange','indigo'] 1
# for player,color in zip(PLAYER_SCORE,[colors[0],colors[4],'teal',colors[3]] ): #'salmon' crimson [default,'teal','orange','indigo'] 3
# for player,color in zip(PLAYER_SCORE,[colors[0],colors[3],'teal',colors[4]] ):4
# for player,color in zip(PLAYER_SCORE,[colors[4],colors[0],'crimson','teal',] ):
