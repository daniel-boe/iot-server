from fastserver import db_manager
from fastserver import models
from fastserver import config
from loguru import logger as log
from influxdb import InfluxDBClient

#TODO [add way to select data handlers in config]

def insert_data_to_local(data: models.RawDeviceRecord | models.RawDeviceRecordMany):
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

    db_manager.get_db().executemany(q,records)
    db_manager.close_db()
    


def handle_influx(*args,**kwargs):
    result = False

    log.info('Forwarding Data to InfluxDB')
    q = 'SELECT *, ROWID FROM sensorDataSyncInflux LIMIT 5'
    data = db_manager.get_db().execute(q).fetchall()
    db_manager.close_db()
    data = [models.TableRecord(**r) for r in data]
    row_ids = [[r.rowid] for r in data]
    data = [r.to_influx() for r in data]
    log.info(f'Found {len(row_ids)} records for InfluxDB')
    
    client = InfluxDBClient(
        host = config.INFLUX_HOST,
        port = config.INFLUX_PORT,
        username = config.INFLUX_USER,
        password = config.INFLUX_PASS,
        database = config.INFLUX_DB
    )

    try:        
        result = client.write_points(data,time_precision='s', batch_size = 100)
    except Exception as ex:
        log.exception()
    
    client.close()

    if result:
        log.info(f'Deleting {row_ids} from sync table')
        q = "DELETE FROM sensorDataSyncInflux WHERE ROWID=?"
        db_manager.get_db().executemany(q,row_ids)
    else:
        log.error('Writing to influx failed')

    db_manager.close_db()

