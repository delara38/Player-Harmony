import pandas as pd

for i in range(5):
    year = (219 - i)*100000 + 1

    shifts_in_y = []

    for j in range(1230):
        try:
            g_id = year + j

            game = pd.read_csv('games/game_{}.csv'.format(g_id),index_col=0)
            shifts_in_y.append(game)
        except:
            print(g_id)
    y = pd.concat(shifts_in_y)
    y.to_csv('season_{}.csv'.format(19-i))
