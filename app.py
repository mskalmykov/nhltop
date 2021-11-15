from flask import Flask, request
from markupsafe import escape

app = Flask(__name__)

@app.route('/')
def rt_main():
    return '<p>Main page</p>'

@app.route('/update/')
def rt_update():
    return '<p>Database is to be updated by this function</p>'

@app.route('/stats/', methods=['GET'])
def rt_stats():
    gamePk = request.args.get('gamePk', 0, type=int)
    personId = request.args.get('personId', 0, type=int)
    return(f'<p>gamePk = {gamePk}</p>\n<p>personId = {personId}</p>')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
