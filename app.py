from flask import Flask, request
from markupsafe import escape
import mariadb
import nhltop

app = Flask(__name__)

@app.route('/')
def rt_main():
    # Try to connect to DB server
    try:
        db_conn = nhltop.db_connect()
    except mariadb.Error as err:
        return f'<p>Error no: {err.errno}, msg: {err.msg}</p>'

    # Update schema if needed
    nhltop.db_update_schema(db_conn)

    seasons = nhltop.db_get_seasons(db_conn)

    body = '<h1>Players, who took part both in All-stars and Final games:</h1>\n'

    for season in seasons['seasons']:
        body = body + f'<h2>Season: {season}</h2>\n'

        top_players = nhltop.db_get_top_players(db_conn, season)
        for player in top_players['players']:
            gamePk = player['gamePk']
            personId = player['personId']

            body = body + f'<p>gamePk = {gamePk}</p>\n'
            body = body + f'<p>personId = {personId}</p>\n'
            body = body + '<p>' + \
                str(nhltop.db_get_player_stat(db_conn, personId, gamePk)) + '</p>\n'
            body = body + '<p>' + \
                str(nhltop.db_get_game(db_conn, gamePk)) + '</p>\n'

    return body

# Health check page
@app.route('/check/')
def rt_check():
    return 'ok'

@app.route('/update/')
def rt_update():
    # Try to connect to DB server
    try:
        db_conn = nhltop.db_connect()
    except mariadb.Error as err:
        return f'<p>Error no: {err.errno}, msg: {err.msg}</p>'

    # Update schema if needed
    nhltop.db_update_schema(db_conn)

    seasons_count = request.args.get('count', 3, type=int)
    seasons = nhltop.get_last_seasons(seasons_count)

    for season in seasons:
        all_stars_games = nhltop.get_season_games(season, 'A')
        playoff_games = nhltop.get_season_games(season, 'P')

        final_games = []
        for game in playoff_games:
            if str(game['gamePk'])[7] == '4':
                final_games.append(game)

        for game in all_stars_games + final_games:
            players = nhltop.get_game_players(game['gamePk'])
            nhltop.db_store_game(db_conn, game)
            for p in players:
                nhltop.db_store_player_stat(db_conn, game, p)

    db_conn.close()
    return '<p>Database is updated</p>'

@app.route('/stats/', methods=['GET'])
def rt_stats():
    # Try to connect to DB server
    try:
        db_conn = nhltop.db_connect()
    except mariadb.Error as err:
        return f'<p>Error no: {err.errno}, msg: {err.msg}</p>'

    # Update schema if needed
    nhltop.db_update_schema(db_conn)

    # Parse arguments
    gamePk = request.args.get('gamePk', 0, type=int)
    personId = request.args.get('personId', 0, type=int)

    body = '<h1>Final game statistics:</h1>\n'

    body = body + '<p>' + \
        str(nhltop.db_get_player_stat(db_conn, personId, gamePk)) + '</p>\n'
    body = body + '<p>' + \
        str(nhltop.db_get_game(db_conn, gamePk)) + '</p>\n'

    return body


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
