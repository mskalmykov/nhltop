#!/usr/bin/env python
import requests
import sys
import os
import mariadb


def get_last_seasons(count):
    result = []

    # Get no more than 15 seasons, and no less than 1
    if count < 1: count = 1
    if count > 15: count = 15

    baseurl = 'https://statsapi.web.nhl.com/api/v1/seasons/'
    reply = requests.get(baseurl + 'current').json()
    current_season = reply['seasons'][0]['seasonId']

    reply = requests.get(baseurl).json()
    if reply['seasons'][-1]['seasonId'] == current_season:
        last = -2
    else:
        last = -1
    for idx in range(last-count+1, last+1):
        result.append(reply['seasons'][idx]['seasonId'])

    return result

def get_season_games(season, type):
    result = []
    baseurl = 'https://statsapi.web.nhl.com/api/v1/schedule?'
    reply = requests.get(baseurl + 'season=' + season + '&gameType=' + type).json()
    for date in reply['dates']:
      for game in date['games']:
        game['gameDate'] = date['date']  # replace gameDate with correct date (start of the game)
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

def db_connect():
    username = os.environ.get('db_user')
    password = os.environ.get('db_password')
    host = os.environ.get('db_server')

    return mariadb.connect(
        username = username,
        password = password,
        host = host,
        database = 'nhltop'
    )

def db_store_game(conn, game):
    cur = conn.cursor()
    cur.execute("""
        REPLACE INTO games (
           gamePk,
           season,
           gameType,
           gameDate,
           team_away_id,
           team_away_name,
           team_away_score,
           team_home_id,
           team_home_name,
           team_home_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
           game['gamePk'],
           game['season'],
           game['gameType'],
           game['gameDate'],
           game['teams']['away']['team']['id'],
           game['teams']['away']['team']['name'],
           game['teams']['away']['score'],
           game['teams']['home']['team']['id'],
           game['teams']['home']['team']['name'],
           game['teams']['home']['score']
        )
    )

def db_store_player_stat(conn, game, player):
    cur = conn.cursor()

    # Save personal info
    cur.execute("""
        REPLACE INTO players (
           gamePk,
           personId,
           fullName,
           birthDate,
           birthCity,
           birthCountry,
           nationality,
           jerseyNumber,
           positionName
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
           game['gamePk'],
           player['person']['id'],
           player['person']['fullName'],
           player['person']['birthDate'],
           player['person']['birthCity'],
           player['person']['birthCountry'],
           player['person']['nationality'],
           player['jerseyNumber'],
           player['position']['name']
        )
    )
    # Save goalie stats
    if player['position']['name'] == 'Goalie':
        cur.execute("""
            REPLACE INTO goalieStats (
               gamePk,
               personId,
               timeOnIce,
               assists,
               goals,
               pim,
               shots,
               saves,
               powerPlaySaves,
               shortHandedSaves,
               evenSaves,
               shortHandedShotsAgainst,
               evenShotsAgainst,
               powerPlayShotsAgainst,
               savePercentage
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
               game['gamePk'],
               player['person']['id'],
               player['stats']['goalieStats']['timeOnIce'],
               player['stats']['goalieStats']['assists'],
               player['stats']['goalieStats']['goals'],
               player['stats']['goalieStats']['pim'],
               player['stats']['goalieStats']['shots'],
               player['stats']['goalieStats']['saves'],
               player['stats']['goalieStats']['powerPlaySaves'],
               player['stats']['goalieStats']['shortHandedSaves'],
               player['stats']['goalieStats']['evenSaves'],
               player['stats']['goalieStats']['shortHandedShotsAgainst'],
               player['stats']['goalieStats']['evenShotsAgainst'],
               player['stats']['goalieStats']['powerPlayShotsAgainst'],
               player['stats']['goalieStats']['savePercentage']
            )
        )
    # Save skater stats
    else:
        cur.execute("""
            REPLACE INTO skaterStats (
               gamePk,
               personId,
               timeOnIce,
               assists,
               goals,
               shots,
               hits,
               powerPlayGoals,
               powerPlayAssists,
               penaltyMinutes,
               faceOffWins,
               faceoffTaken,
               takeaways,
               giveaways,
               shortHandedGoals,
               shortHandedAssists,
               blocked,
               plusMinus,
               evenTimeOnIce,
               powerPlayTimeOnIce,
               shortHandedTimeOnIce
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
               game['gamePk'],
               player['person']['id'],
               player['stats']['skaterStats']['timeOnIce'],
               player['stats']['skaterStats']['assists'],
               player['stats']['skaterStats']['goals'],
               player['stats']['skaterStats']['shots'],
               player['stats']['skaterStats']['hits'],
               player['stats']['skaterStats']['powerPlayGoals'],
               player['stats']['skaterStats']['powerPlayAssists'],
               player['stats']['skaterStats']['penaltyMinutes'],
               player['stats']['skaterStats']['faceOffWins'],
               player['stats']['skaterStats']['faceoffTaken'],
               player['stats']['skaterStats']['takeaways'],
               player['stats']['skaterStats']['giveaways'],
               player['stats']['skaterStats']['shortHandedGoals'],
               player['stats']['skaterStats']['shortHandedAssists'],
               player['stats']['skaterStats']['blocked'],
               player['stats']['skaterStats']['plusMinus'],
               player['stats']['skaterStats']['evenTimeOnIce'],
               player['stats']['skaterStats']['powerPlayTimeOnIce'],
               player['stats']['skaterStats']['shortHandedTimeOnIce']
            )
        )

# Retrieve players, who played both All-stars and Final games of the season
def get_top_players(conn, season):
    cur = conn.cursor()
    result = {'players': []}

    cur.execute("""
        WITH q1 AS
         (SELECT p.personId,
                 p.gamePk,
                 g.gameType,
                 g.season 
          FROM players p INNER JOIN games g ON p.gamePk = g.gamePk WHERE g.gameType = 'P'),
        q2 AS
         (SELECT p.personId,
                 p.gamePk, 
                 g.gameType,
                 g.season 
         FROM players p INNER JOIN games g ON p.gamePk = g.gamePk WHERE g.gameType = 'A')
        SELECT DISTINCT
          q1.personId,
          q1.season
        FROM q1 INNER JOIN q2 ON q1.personId = q2.personId AND q1.season = q2.season
        WHERE q1.season = ?
        """,
        (season,)
    )

    players = []
    for (personId, season) in cur:
        players.append(personId)

    for player in players:
        cur.execute("""
            SELECT p.personId, p.gamePk, g.gameType, g.season 
            FROM players p INNER JOIN games g ON p.gamePk = g.gamePk
            WHERE g.gameType = 'P' AND p.personId = ? AND g.season = ?
            ORDER BY g.gamePk DESC LIMIT 1""",
            (player, season)
        )
        for (personId, gamePk, gameType, season) in cur:
            result['players'].append({'personId': personId, 'gamePk': gamePk})

    return result

# Entry point
db_conn = db_connect()

#season = sys.argv[1]

seasons = get_last_seasons(3)
for season in seasons:
    all_stars_games = get_season_games(season, 'A')
    playoff_games = get_season_games(season, 'P')

final_games = []
for game in playoff_games:
    if str(game['gamePk'])[7] == '4':
        final_games.append(game)

for game in all_stars_games + final_games:
    db_store_game(db_conn, game)

    players = get_game_players(game['gamePk'])
    for p in players:
        db_store_player_stat(db_conn, game, p)

print('Players, who took part both in All-stars and Final games:')
for season in seasons:
    print(f'Season: {season}')
    print(get_top_players(db_conn, season))

