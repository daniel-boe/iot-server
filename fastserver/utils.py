import datetime as dt
from sqlite3 import Row
from devtools import debug
from fastserver import models
from sqlite3 import Connection
from pydantic import parse_obj_as

def get_data_for_id(db:Connection, device_id:str|None, n:int) -> list[models.TableRecord]:
    if device_id:
        q = f"""SELECT * FROM sensorData where device_id='{device_id}'
            ORDER BY tmeas DESC LIMIT {n}"""
    else:
        q = f"""SELECT * FROM sensorData
            ORDER BY tmeas DESC LIMIT {n} """
    data = db.execute(q).fetchall()
    if data:
        return parse_obj_as(list[models.TableRecord],data)
    else:
        return []
    
def get_recent_data(db:Connection,
                    seconds_ago:int,
                    device_ids:list[str]|None=None) -> list[models.TableRecord]:
    q = f"""SELECT * FROM sensorData 
            WHERE TMEAS between 
            '{(dt.datetime.utcnow() - dt.timedelta(seconds=seconds_ago)).isoformat(sep=' ')}'
            AND '{dt.datetime.utcnow().isoformat(sep=' ')}'"""
    if device_ids:
        # Note, if there is only 1 element int the tuple, repr adds a trailing comma
        q += f'\nAND device_id IN {repr(tuple(device_ids)).replace(",)", ")")}'
    data = db.execute(q).fetchall()
    if data:
        return parse_obj_as(list[models.TableRecord],data)
    else:
        return []
    
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
