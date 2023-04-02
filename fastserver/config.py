from pathlib import Path
from dotenv import load_dotenv
from os import environ, path

basedir =  path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir,'deploy','.env'))

DB_LOC = Path('fastserver','db.sqlite')
DB_SCHEMA = Path('fastserver','schema.sql')
INFLUX_MEASUREMENT = environ.get('INFLUX_MEAS')
INFLUX_HOST = environ.get('INFLUX_HOST')
INFLUX_PORT = int(environ.get('INFLUX_PORT'))
INFLUX_USER = environ.get('INFLUX_USER')
INFLUX_PASS = environ.get('INFLUX_PASS')
INFLUX_DB = environ.get('INFLUX_DB')
DATA_HANDLERS = ['mariadb']

MARIA_USER=environ.get('MARIA_USER')
MARIA_PASSWORD=environ.get('MARIA_PASSWORD')
MARIA_HOST=environ.get('MARIA_HOST')
MARIA_PORT=int(environ.get('MARIA_PORT'))
MARIA_DATABASE=environ.get('MARIA_DATABASE')
MARIA_TABLE=environ.get('MARIA_TABLE')