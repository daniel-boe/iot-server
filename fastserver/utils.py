import models
import datetime as dt
from sqlite3 import Row, Connection
from loguru import logger as log

def utc_time(no_tz=True):
    tz=dt.timezone.utc
    if no_tz:
        return dt.datetime.now(tz).replace(tzinfo=None)
    else:
        return dt.datetime.now(tz)     

def get_data_for_id(db:Connection, device_id:str|None, n:int) -> list[models.TableRecord]:
    if device_id:
        q = f"""SELECT * FROM sensorData where device_id='{device_id}'
            ORDER BY tmeas DESC LIMIT {n}"""
    else:
        q = f"""SELECT * FROM sensorData
            ORDER BY tmeas DESC LIMIT {n} """
    data = db.execute(q).fetchall()
    if data:
        return models.TableRecordList.validate_python(data)
    else:
        return []
    
def get_recent_data(db:Connection,
                    seconds_ago:int,
                    device_ids:list[str]|None=None) -> list[models.TableRecord]:
    q = f"""SELECT * FROM sensorData 
            WHERE TMEAS between 
            '{(utc_time() - dt.timedelta(seconds=seconds_ago)).isoformat(sep=' ')}'
            AND '{utc_time().isoformat(sep=' ')}'"""
    if device_ids:
        # Note, if there is only 1 element int the tuple, repr adds a trailing comma
        q += f'\nAND device_id IN {repr(tuple(device_ids)).replace(",)", ")")}'
    data = db.execute(q).fetchall()
    if data:
        return models.TableRecordList.validate_python(data)
    else:
        return []
    
def get_latest_rn(db:Connection) -> int:
    q = """SELECT rowid FROM sensorData order by rowid desc limit 1;"""
    
    data = db.execute(q).fetchone()
    if data:
        return data['rowid']
    else:
        return 0

def get_unique_devices(db:Connection) -> list[Row]:
    q = """SELECT device_id,  strftime('%s','now') - strftime('%s',MAX(tmeas)) as last_heard_sec from sensorData GROUP BY device_id"""
    
    data = db.execute(q).fetchall()
    if data:
        return data
    else:
        return []
    
def get_last_measurements(db:Connection) -> list[Row]:
    q = """SELECT X.device_id, strftime('%s','now') - strftime('%s',X.tmeas) as seconds_ago,
                 X.sensor_name, round(X.sensor_value,2) as value
       FROM sensorData X 
            join 
            (SELECT device_id, MAX(tmeas) as tmeas FROM sensorData GROUP BY device_id) Y
            ON X.device_id = y.device_id and X.tmeas = Y.tmeas
       """
    
    data = db.execute(q).fetchall()
    if data:
        return data
    else:
        return []
