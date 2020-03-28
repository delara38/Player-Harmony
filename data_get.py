import pandas as pd
import nba_scraper.nba_scraper as ns
import datetime
from math import ceil
import numpy as np
from  os import path

def seconds(x):
    periods = x['period']*12*60
    cur = datetime.datetime.strptime(x['pctimestring'], "%M:%S") - datetime.datetime(1900,1,1)
    if x['period'] == 5:
        return -1 * cur.total_seconds()
    return cur.total_seconds() + periods

def find_pos(x):
    n =   ceil(x/3)
    if n > 5:
        n = 5
    if n < -5:
        n = 5
    return n

def count_pos(x, t):
    last = x.iloc[0,:]['event_team']
    n = 0
    if t == 'a':

        n = 1 if last == x.iloc[0,:]['away_team_abbrev'] else 0

        for i in range(1, len(x)):
            if x.iloc[i,:]['event_team'] != last and x.iloc[i,:]['event_type_de'] != 'foul':
                last = x.iloc[i,:]['event_team']
                if x.iloc[i,:]['away_team_abbrev'] == x.iloc[i,:]['event_team']:
                    n += 1
    else:

        n = 1 if last == x.iloc[0,:]['home_team_abbrev'] else 0

        for i in range(1, len(x)):
            if x.iloc[i,:]['event_team'] != last and x.iloc[i,:]['event_type_de'] != 'foul':
                last = x.iloc[i,:]['event_team']
                if x.iloc[i,:]['home_team_abbrev'] == x.iloc[i,:]['event_team']:
                    n+=1
    return n



for i in range(973, 1230):

    g_id = 21900001 + i

    if not path.exists("games/game_{}.csv".format(g_id)):

        n = ns.scrape_game([g_id])
        n['timeLeft'] = n.apply(seconds, axis=1)
        n['isHome'] = n.apply(lambda x: 1 if x['home_team_abbrev'] == x['event_team'] else 0,axis=1)
        n['h_points_made'] = n.apply(lambda x: x['points_made'] if x['home_team_abbrev'] == x['event_team'] else 0, axis=1)
        n['a_points_made'] = n.apply(lambda x: x['points_made'] if x['away_team_abbrev'] == x['event_team'] else 0, axis=1)
        n['h_points'] = n['h_points_made'].cumsum()
        n['a_points'] = n['a_points_made'].cumsum()

        n['h_point_dif'] = n.apply(lambda x: x['h_points'] - x['a_points'], axis=1)
        n['a_point_dif'] = n.apply(lambda x: x['a_points'] - x['h_points'], axis=1)
        n = n[(n['event_type_de'] != 'jump-ball')&(n['event_type_de'] != 'period-end')]


        subs = n[(n['event_type_de'] == 'period_start')|(n['event_type_de'] == 'substitution')].index.tolist()


        shifts  = []
        for ind in range(len(subs)):
            if ind == 0:
                shifts.append(n.iloc[:subs[ind],:])
            else:
                arr = n.iloc[subs[ind-1]+1:subs[ind],:]
                if len(arr) != 0:
                    shifts.append(arr)

        all_shifts = []

        for i in range(len(shifts)):
            shift = shifts[i]

            time_d = shift.iloc[-1,:]['seconds_elapsed'] - shift.iloc[0,:]['seconds_elapsed']
            pos_passed_h = count_pos(shift, 'h')
            pos_passed_a = count_pos(shift, 'a')

            h_players = shift.iloc[0,:][['home_player_1_id','home_player_2_id','home_player_3_id',
                                         'home_player_4_id','home_player_5_id']]

            a_players = shift.iloc[0,:][['away_player_1_id','away_player_2_id','away_player_3_id',
                                         'away_player_4_id','away_player_5_id']]

            home_points = shift[shift['isHome'] == 1].sum()['points_made']
            away_points = shift[shift['isHome'] == 0].sum()['points_made']

            home_start = shift.iloc[0,:]['isHome']
            away_start = 1 - shift.iloc[0,:]['isHome']


            pd_h = shift.iloc[0,:]['h_point_dif'] + shift.iloc[0,:]['a_points_made'] - shift.iloc[0,:]['h_points_made']
            pos_points_h = find_pos(pd_h)

            pd_a = shift.iloc[0,:]['a_point_dif'] + shift.iloc[0,:]['h_points_made'] - shift.iloc[0,:]['a_points_made']
            pos_points_a = find_pos(pd_a)

            try:
                Y_h = home_points / pos_passed_h * 100
            except:
                Y_h = 0
            try:
                Y_a = away_points / pos_passed_a * 100
            except:
                Y_a = 0



            home_info = pd.Series(np.array([Y_h, 1, pos_points_h, time_d, home_start] +
                                           h_players.values.tolist() +
                                           a_players.values.tolist()),
                                  index=['PTS/100','isHome','possession_diff','time','startsBall','offence1',
                                         'offence2','offence3','offence4','offence5','defence1','defence2',
                                         'defence3','defence4','defence5'])
            away_info = pd.Series(np.array([Y_a, 0, pos_points_a, time_d, away_start] +
                                           a_players.values.tolist() +
                                           h_players.values.tolist()),
                                  index=['PTS/100','isHome','possession_diff','time','startsBall','offence1',
                                         'offence2','offence3','offence4','offence5','defence1','defence2',
                                         'defence3','defence4','defence5'])

            all_shifts.append(home_info)
            all_shifts.append(away_info)

        game_shifts = pd.concat(all_shifts, axis=1).transpose()

        game_shifts.to_csv('games/game_{}.csv'.format(g_id))
