import flask
from flask import request, jsonify
import pyodbc
from constants import values
from flask_cors import CORS


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['JSON_SORT_KEYS'] = False
CORS(app)


def teste():
    return


@app.route('/', methods=['GET'])
def home():
    return '''<h1>SmartStudyRooms</h1>
<p><a href="http://smartrooms.ddns.net:5000/api/events">Get All Events</a> </p>
<p><a href="http://smartrooms.ddns.net:5000/api/rooms">Get All Rooms</a></p>
<p><a href="http://smartrooms.ddns.net:5000/api/rooms/occupation">Get All Rooms Occupation</a></p>
<p><a href="http://smartrooms.ddns.net:5000/api/room/0/last-event">Get Room &lt;id&gt; Last Event</a></p>
<p><a href="http://smartrooms.ddns.net:5000/api/room/0/events/2018-11-01T00:00:00/2018-12-11T00:00:00">Get Room &lt;id&gt; events From &lt;date&gt; TO &lt;date&gt;</a></p>
<p><a href="http://smartrooms.ddns.net:5000/api/room/0/predict">Get Room &lt;id&gt; Predict</a></p>

 '''


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


@app.route('/api/rooms/occupation', methods=['GET'])
def api_all_rooms_occupation():
    conn = pyodbc.connect(values.connection_string)
    cur = conn.cursor()

    query = ''
    for i in range(4):
        query += 'SELECT nome_sala, occupied_seats, empty_seats ' \
                 'FROM (SELECT TOP 1 TBL_Salas.nome_sala, TBL_Salas_id, occupied_seats, empty_seats, time ' \
                 'FROM TBL_Eventos, TBL_Salas ' \
                 'WHERE TBL_Salas.id = TBL_Eventos.TBL_Salas_id AND TBL_Salas_id = TBL_Salas.id ' \
                 'AND TBL_Salas_id = %s ORDER BY time DESC) as query%s ' % (i, i)
        if i <= 2:
            query += " UNION ALL "
    print(query)
    all_rooms = cur.execute(query).fetchall()

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
    query = "SELECT * FROM TBL_Eventos WHERE TBL_Salas_id = " + id_room + " AND time > '" + date_from + \
            "' AND time < '" + date_to + "' ORDER BY time DESC"

    print(date_from)
    print(date_to)

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
    query = "SELECT empty_seats, occupied_seats, time FROM TBL_Eventos WHERE TBL_Salas_id = " + id_room + \
            " ORDER BY time DESC"

    conn = pyodbc.connect(values.connection_string)
    cur = conn.cursor()

    all_results = cur.execute(query).fetchall()
    columns = [column[0] for column in cur.description]

    data = []
    for row in all_results:
        data.append(dict(zip(columns, list(row))))

    return jsonify(data)


app.run(host='0.0.0.0')
