import flask
from flask import request, jsonify
import pyodbc
from constants import values
from flask_cors import CORS


app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['JSON_SORT_KEYS'] = False
CORS(app)


@app.route('/', methods=['GET'])
def home():
    return '''<h1>SmartStudyRooms</h1>
<p><a href="http://smartrooms.ddns.net:5000/api/events">Get All Events</a> </p>
<p><a href="http://smartrooms.ddns.net:5000/api/rooms">Get All Rooms</a></p>
<p><a href="http://smartrooms.ddns.net:5000/api/rooms/occupation">Get All Rooms Occupation</a></p>
<p><a href="http://smartrooms.ddns.net:5000/api/room/0/last-event">Get Room &lt;id&gt; Last Event</a></p>
<p><a href="http://smartrooms.ddns.net:5000/api/room/0/events/2018-11-01T00:00:00/2018-12-11T00:00:00">Get Room &lt;id&gt; events From &lt;date&gt; TO &lt;date&gt;</a></p>
<p><a href="http://smartrooms.ddns.net:5000/api/room/0/predict">Get Room &lt;id&gt; Predict</a></p>
<p><a href="http://smartrooms.ddns.net:5000/api/rooms/occupation/daily">Get daily occupation(week_day=(1-Monday;2-Tuesday,...)</a></p>
<p><a href="http://smartrooms.ddns.net:5000/api/services/status">Get services status</a></p>
<p><a href="http://smartrooms.ddns.net:5000/api/subscribed/<email>/<room0>/<room1>/<room2>/<room3>">subscribe</a></p>

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


@app.route('/api/rooms/occupation/daily', methods=['GET'])
def api_room_daily_occupation():
    query = "SELECT TBL_Salas_id as id_room, " \
            "DATEPART(WEEKDAY,time) as week_day, AVG(occupied_seats) as occupied_seats_avg, AVG(empty_seats) " \
            "as empty_seats_avg FROM TBL_Eventos WHERE DATEPART(HOUR,time) > 8 AND " \
            "DATEPART(HOUR,time) < 19 GROUP BY TBL_Salas_id,DATEPART(WEEKDAY, time)"

    conn = pyodbc.connect(values.connection_string)
    cur = conn.cursor()

    all_results = cur.execute(query).fetchall()
    columns = [column[0] for column in cur.description]

    data = []
    for row in all_results:
        data.append(dict(zip(columns, list(row))))

    return jsonify(data)


@app.route('/api/room/<id_room>/predict', methods=['GET'])
def api_room_prediction(id_room):
    query = ("SELECT"
             " DATEPART(HOUR, time) as hour,"
             " AVG(occupied_seats) as occupied_seats_avg,"
             " AVG(empty_seats) as empty_seats_avg "
             "FROM TBL_Eventos "
             "WHERE "
             "TBL_Salas_id = " + id_room + " "
             "AND time > DATEADD(day, -14, CURRENT_TIMESTAMP) "
             "GROUP BY TBL_Salas_id, DATEPART(HOUR, time) "
             "ORDER BY hour ASC")

    conn = pyodbc.connect(values.connection_string)
    cur = conn.cursor()

    all_results = cur.execute(query).fetchall()
    columns = [column[0] for column in cur.description]

    data = []
    for row in all_results:
        data.append(dict(zip(columns, list(row))))

    return jsonify(data)


# @app.route('/api/services/status', methods=['GET'])
# def api_services_status():
#     query = ("SELECT TBL_Services.name,TBL_Services_Updates.status,TBL_Services_Updates.last_update "
#              "FROM TBL_Services,TBL_Services_Updates "
#              "WHERE TBL_Services.id = TBL_Services_Updates.service_id AND "
#              "TBL_Services_Updates.last_update =(select max(TBL_Services_Updates.last_update) "
#              "FROM TBL_Services_Updates);")
#
#     conn = pyodbc.connect(values.connection_string)
#     cur = conn.cursor()
#
#     all_results = cur.execute(query).fetchall()
#     columns = [column[0] for column in cur.description]
#
#     data = []
#     for row in all_results:
#         data.append(dict(zip(columns, list(row))))
#
#     return jsonify(data)


@app.route('/api/services/status', methods=['GET'])
def api_services_status():
    query = ("SELECT TBL_Services.id, TBL_Services.name, "
             "SUM(CASE WHEN TBL_Services_Updates.status='Ok' THEN 1 ELSE 0 END) as ok_status, "
             "SUM(CASE WHEN TBL_Services_Updates.status='Dead' THEN 1 ELSE 0 END) as dead_status "
             "FROM TBL_Services, TBL_Services_Updates "
             "WHERE TBL_Services.id = TBL_Services_Updates.service_id "
             "GROUP BY TBL_Services.name, TBL_Services.id")

    conn = pyodbc.connect(values.connection_string)
    cur = conn.cursor()

    all_results = cur.execute(query).fetchall()

    get_service_names = "SELECT TOP (SELECT COUNT(*) FROM TBL_Services) * FROM TBL_Services_Updates " \
                        "ORDER BY last_update DESC"

    all_services = cur.execute(get_service_names).fetchall()

    services = []
    for line in all_services:
        services.append(line)

    data_status = []
    for row in all_services:
        data_status.append([row[1], row[2]])

    columns = ['service_id', 'name', 'status', 'uptime']

    data = []
    for row in all_results:
        for i in range(len(data_status)):
            if int(data_status[i][0]) == int(row[0]):
                uptime = str(round(100 * (row[2] / (row[3] + row[2])), 4)) + " %"
                linha = [row[0], row[1], data_status[i][1], uptime]
                data.append(dict(zip(columns, list(linha))))

    return jsonify(data)


@app.route('/api/subscribed/<email>/<room0>/<room1>/<room2>/<room3>', methods=['GET'])
def api_subscribed(email, room0, room1, room2, room3):
    # Verifica se o user existe
    query = "SELECT id from TBL_Account WHERE email='" + str(email) + "'"
    conn = pyodbc.connect(values.connection_string)
    cur = conn.cursor()
    query_user = cur.execute(query).fetchall()
    for row in query_user:
        id = list(row)
    # Se o user nao existir
    if not query_user:
        # Insere
        query = "INSERT INTO TBL_Account VALUES ('" + str(email) + "')"
        conn = pyodbc.connect(values.connection_string)
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        # Pega o id que inseriu
        query = "SELECT id from TBL_Account WHERE email='" + str(email) + "'"
        conn = pyodbc.connect(values.connection_string)
        cur = conn.cursor()
        query_user = cur.execute(query).fetchall()
        for row in query_user:
            id = list(row)
    # Elimina os registos antigos
    query = "DELETE from TBL_Account_has_TBL_Salas WHERE TBL_Account_id='"+str(id[0])+"'"
    conn = pyodbc.connect(values.connection_string)
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()
    # Insere os novos dados
    if int(room0) == 1:
        insert_user_rooms(id, 0)
    if int(room1) == 1:
        insert_user_rooms(id, 1)
    if int(room2) == 1:
        insert_user_rooms(id, 2)
    if int(room3) == 1:
        insert_user_rooms(id, 3)
    return jsonify("Registered successfully")


def insert_user_rooms(par_user_id, par_room_id):
    query = "INSERT INTO TBL_Account_has_TBL_Salas VALUES ('"+str(par_user_id[0])+"','"+str(par_room_id)+"')"
    conn = pyodbc.connect(values.connection_string)
    cur = conn.cursor()
    cur.execute(query)
    conn.commit()


app.run('0.0.0.0')
