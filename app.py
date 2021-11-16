from flask import Flask, request
from markupsafe import escape
import mariadb
import nhltop

app = Flask(__name__)

@app.route('/')
def rt_main():
    return '<p>Main page</p>'

@app.route('/update/')
def rt_update():
    # Try to connect to DB server
    try:
        db_conn = nhltop.db_connect()
    except mariadb.Error as err:
        return f'<p>Error no: {err.errno}, msg: {err.msg}</p>'
        exit(1)

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
    gamePk = request.args.get('gamePk', 0, type=int)
    personId = request.args.get('personId', 0, type=int)
    return(f'<p>gamePk = {gamePk}</p>\n<p>personId = {personId}</p>')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
