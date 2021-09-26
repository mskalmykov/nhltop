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

print('Final games:')
for game in final_ids:
    info = get_game_brief(game)
    print('{}: {:30} - {:30}   {}:{}'.format(game, *info))


#for date in games['dates']:
#  for game in date['games']:
#    gamePk = game['gamePk']
#    team_away_name = game['teams']['away']['team']['name']
#    team_away_score = game['teams']['away']['score']
#    team_home_name = game['teams']['home']['team']['name']
#    team_home_score = game['teams']['home']['score']
#    print('{}: {} - {} {}:{}'.format(gamePk, team_away_name, team_home_name, team_away_score, team_home_score))
