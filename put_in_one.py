import pandas as pd


all = []
for i in range(15,20):
    all.append(pd.read_csv("season_{}.csv".format(i)))
n = pd.concat(all)
n.to_csv('five_year_shifts.csv')
print('yeeee')