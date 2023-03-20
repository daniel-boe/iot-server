import datetime as dt
import sqlite3
import click
from flask.cli import with_appcontext
from flask import current_app, g

def get_db():
    """
        Creates a connection to the local db and stuffs it into the global context.
        Thus, the same connection will be used throughout a request
    """
    
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES # Tell sqlite to parse as declared types
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    """
        Should be called once time at app initialization.  Communicates with remote DB and copies over all serial number data to a local
    """
    print('Initializing the DB')
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    """Register database functions with the Flask app. This is called by
    the application factory.
    """
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def insert_sensor_data(host,tmeas,sensor_data):
    print('Adding Sensor data')
    table='sensorData'
    conn = get_db()
    cursor=conn.cursor()
    tmeas = dt.datetime.fromtimestamp(tmeas).strftime('%Y-%m-%d %X')      
    for k,v in sensor_data.items():
        values=(tmeas,host,k,v)
        sql_command=f'INSERT INTO {table} (tmeas,host,sensor_name,sensor_value) VALUES {values}'
        cursor.execute(sql_command)
    conn.commit()
    cursor.close()
    conn.close()

def handle_sensor_json(data):
    print(data)
    try:
        insert_sensor_data(**data)
    except Exception as ex:
        print('Error when inserting into sqliteDB')
        print(ex)
