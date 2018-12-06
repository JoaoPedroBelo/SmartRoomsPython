import flask
from flask import request, jsonify
import pyodbc
from constants import values


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['JSON_SORT_KEYS'] = False


@app.route('/', methods=['GET'])
def home():
    return '''<h1>SmartStudyRooms</h1>
<p>An API.</p>'''


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/api/events', methods=['GET'])
def api_all_events():
    conn = pyodbc.connect(values.connection_string)
    cur = conn.cursor()
    all_events = cur.execute('SELECT * FROM TBL_Eventos ORDER BY time DESC;').fetchall()

    data = []
    columns = [column[0] for column in cur.description]

    for row in all_events:
        data.append(dict(zip(columns, list(row))))

    return jsonify(data)


@app.route('/api/rooms', methods=['GET'])
def api_all_rooms():
    conn = pyodbc.connect(values.connection_string)
    cur = conn.cursor()
    all_rooms = cur.execute('SELECT * FROM TBL_Salas;').fetchall()

    data = []
    columns = [column[0] for column in cur.description]

    for row in all_rooms:
        data.append(dict(zip(columns, list(row))))

    return jsonify(data)


@app.route('/api/room/<id_room>/last-event', methods=['GET'])
def api_last_event_by_room(id_room):
    query = "SELECT TOP 1 * FROM TBL_Eventos WHERE TBL_Salas_id = " + id_room + " ORDER BY time DESC"

    conn = pyodbc.connect(values.connection_string)
    cur = conn.cursor()

    all_results = cur.execute(query).fetchall()
    columns = [column[0] for column in cur.description]

    data = []
    for row in all_results:
        data.append(dict(zip(columns, list(row))))

    return jsonify(data)


@app.route('/api/room/<id_room>/events/<date_from>/<date_to>', methods=['GET'])
def api_event_from_to(id_room, date_from, date_to):
    query = "SELECT TOP 1 * FROM TBL_Eventos WHERE TBL_Salas_id = " + id_room + " AND time > " + date_from + \
            " AND time < " + date_to + " ORDER BY time DESC"

    conn = pyodbc.connect(values.connection_string)
    cur = conn.cursor()

    all_results = cur.execute(query).fetchall()
    columns = [column[0] for column in cur.description]

    data = []
    for row in all_results:
        data.append(dict(zip(columns, list(row))))

    return jsonify(data)


@app.route('/api/room/<id_room>/predict', methods=['GET'])
def api_room_predict(id_room):
    query = "SELECT empty_seats, occupied_seats, time FROM TBL_Eventos WHERE TBL_Salas_id = " + id_room + " ORDER BY time DESC"

    conn = pyodbc.connect(values.connection_string)
    cur = conn.cursor()

    all_results = cur.execute(query).fetchall()
    columns = [column[0] for column in cur.description]

    data = []
    for row in all_results:
        data.append(dict(zip(columns, list(row))))

    return jsonify(data)


app.run(host='0.0.0.0')
