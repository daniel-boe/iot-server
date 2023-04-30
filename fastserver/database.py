import contextlib
import sqlite3
from fastserver.config import DB_LOC, DB_SCHEMA, DB_HANDLERS_DIR
from loguru import logger as log
from fastserver import models

def init_db():
    with sqlite3.connect(DB_LOC) as db:
        db.executescript(DB_SCHEMA.read_text())
    db.close()
    DB_HANDLERS_DIR.mkdir(exist_ok=True)


def get_db():
    db = sqlite3.connect(DB_LOC,check_same_thread=False)
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.commit()
        db.close()

@contextlib.contextmanager
def get_db_ctx():
    db = sqlite3.connect(DB_LOC,check_same_thread=False)
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.commit()
        db.close()

def insert_data_to_local(db :sqlite3.Connection ,data: models.RawDeviceRecord | models.RawDeviceRecordMany):
    columns= ('device_id','tmeas','sensor_name','sensor_value')
    q = f"""INSERT INTO sensorData {repr(columns)} VALUES (?,?,?,?)"""
    records = []

    if isinstance(data,models.RawDeviceRecord):
        log.info('Handling RawDeviceRecord')
        for k,v in data.measurements.items():
            records.append((data.device_id,data.tmeas,k,v))

    elif isinstance(data,models.RawDeviceRecordMany):
        log.info('Handling RawDeviceRecordMany')
        for sample in data.samples:
            for k,v in sample.measurements.items():
                records.append((data.device_id,sample.tmeas,k,v))
    else:
        log.error('Invalid data model received')

    if not records:
        return True
    db.executemany(q,records)
    
if __name__ == '__main__':
    init_db()