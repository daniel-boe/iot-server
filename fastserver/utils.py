from fastserver import models
from sqlite3 import Connection
from pydantic import parse_obj_as

def get_data_for_id(db:Connection,device_id:str) -> list[models.TableRecord]:
    q = f"""SELECT * FROM sensorData where device_id='{device_id}'
            ORDER BY tmeas DESC LIMIT 100 """
    data = db.execute(q).fetchall()
    if data:
        return parse_obj_as(list[models.TableRecord],data)
    else:
        return []