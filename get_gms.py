#!/usr/bin/env python
import requests
import sys

def get_season_games(season, type):
    result = []
    baseurl = 'https://statsapi.web.nhl.com/api/v1/schedule?'
    reply = requests.get(baseurl + 'season=' + season + '&gameType=' + type).json()
    for date in reply['dates']:
      for game in date['games']:
        result.append(game['gamePk'])
    return result

def get_game_brief(game_id):
    result = []
    baseurl = 'https://statsapi.web.nhl.com/api/v1/game/'
    reply = requests.get(baseurl + str(game_id) + '/linescore').json()

    result.append(reply['teams']['home']['team']['name'])
    result.append(reply['teams']['away']['team']['name'])
    result.append(reply['teams']['home']['goals'])
    result.append(reply['teams']['away']['goals'])

    return result


def get_game_players(game_id):
    result = []
    baseurl = 'https://statsapi.web.nhl.com/api/v1/game/'
    reply = requests.get(baseurl + str(game_id) + '/boxscore').json()
    
    team_away = reply['teams']['away']['team']
    team_home = reply['teams']['home']['team']
    players_away = reply['teams']['away']['players']
    players_home = reply['teams']['home']['players']

    for key in players_away.keys():
        player = players_away[key]
        if player['stats']: 
            player['team'] = team_away
            result.append(player)

    for key in players_home.keys():
        player = players_home[key]
        if player['stats']: 
            player['team'] = team_home
            result.append(player)

    return result

# Entry point
season = sys.argv[1]
all_stars_ids = get_season_games(season, 'A')
playoff_ids = get_season_games(season, 'P')

final_ids = []
for game in playoff_ids:
    if str(game)[7] == '4':
        final_ids.append(game)

print('All stars games:')
for game in all_stars_ids:
    info = get_game_brief(game)
    print('{}: {:30} - {:30}   {}:{}'.format(game, *info))
    players = get_game_players(game)
    for p in players:
        print('{:30} {:30}'.format(p['person']['fullName'],p['team']['name']))

print('Final games:')
for game in final_ids:
    info = get_game_brief(game)
    print('{}: {:30} - {:30}   {}:{}'.format(game, *info))
    players = get_game_players(game)
    for p in players:
        print('{:30} {:30}'.format(p['person']['fullName'],p['team']['name']))


