import contextlib
import sqlite3
import models
from pathlib import Path
from config import load_config
from loguru import logger as log

config = load_config()

def init_db():
    with sqlite3.connect(config.local_db.name) as db:
        db.executescript(Path(config.local_db.schema).read_text())
    db.close()
    Path(config.local_db.handlers_dir).mkdir(exist_ok=True)

def get_db():
    db = sqlite3.connect(config.local_db.name,check_same_thread=False)
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.commit()
        db.close()

@contextlib.contextmanager
def get_db_ctx():
    db = sqlite3.connect(config.local_db.name,check_same_thread=False)
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