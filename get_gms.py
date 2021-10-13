#!/usr/bin/env python
import requests
import sys

def get_season_games(season, type):
    result = []
    baseurl = 'https://statsapi.web.nhl.com/api/v1/schedule?'
    reply = requests.get(baseurl + 'season=' + season + '&gameType=' + type).json()
    for date in reply['dates']:
      for game in date['games']:
        result.append(game)
    return result

def print_game_brief(game):
    gamePk = game['gamePk']
    team_away_name = game['teams']['away']['team']['name']
    team_home_name = game['teams']['home']['team']['name']
    team_away_score = game['teams']['away']['score']
    team_home_score = game['teams']['home']['score']
    print('{}: {:30} - {:30}   {}:{}'.format(gamePk, team_away_name, team_home_name, team_away_score, team_home_score))


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
all_stars_games = get_season_games(season, 'A')
playoff_games = get_season_games(season, 'P')

final_games = []
for game in playoff_games:
    if str(game['gamePk'])[7] == '4':
        final_games.append(game)

print('All stars games:')
for game in all_stars_games:
    print_game_brief(game)

    players = get_game_players(game['gamePk'])
    for p in players:
        print('{:30} {:30}'.format(p['person']['fullName'],p['team']['name']))

print('Final games:')
for game in final_games:
    print_game_brief(game)

    players = get_game_players(game['gamePk'])
    for p in players:
        print('{:30} {:30}'.format(p['person']['fullName'],p['team']['name']))


