import abc
from fastserver import models, config
from fastserver.database import get_db_ctx
from loguru import logger as log
from sqlite3 import Connection
from time import sleep

if 'influxdb' in config.DATA_HANDLERS:
    from influxdb import InfluxDBClient

if 'mariadb' in config.DATA_HANDLERS:
    import mariadb

class RemoteDBManager:

    def __init__(self):
        self.handlers = [c for c in RemoteDBHandler.__subclasses__() if c.handles in config.DATA_HANDLERS]

    def handle_data(self,*args,**kwargs):
        log.debug('Handling data plugins')
        for handler in self.handlers:
            with get_db_ctx() as db:
                handler.handle(db)    
        log.debug('Handling Data Plugins complete')


class RemoteDBHandler:

    def __init__(self):
        pass

    @abc.abstractclassmethod
    def handle(self,db:Connection):
        pass


class InfluxHandler(RemoteDBHandler):
    handles = 'influxdb'

    @classmethod
    def handle(cls,db:Connection):
        result = False

        log.info('Forwarding Data to InfluxDB')
        q = 'SELECT *, ROWID FROM sensorDataSyncInflux LIMIT 5'
        data = db.execute(q).fetchall()
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
            db.executemany(q,row_ids)
        else:
            log.error('Writing to influx failed')

class MariaHandler(RemoteDBHandler):
    handles = 'mariadb'

    @classmethod
    def handle(cls,db:Connection):
        result = False

        log.info('Forwarding Data to mariaDB')
        q = 'SELECT *, ROWID FROM sensorDataSyncMaria LIMIT 5'
        data = db.execute(q).fetchall()
        data = [models.TableRecord(**r) for r in data]
        if not data:
            log.warning('No Data found to forward to maria')
            return 
        row_ids = [[r.rowid] for r in data]
        data = [r.to_sql() for r in data]
        log.info(f'Found {len(row_ids)} records for MariaDB')

        conn = mariadb.connect(
            user=config.MARIA_USER,
            password=config.MARIA_PASSWORD,
            host=config.MARIA_HOST,
            port=config.MARIA_PORT,
            database=config.MARIA_DATABASE
        )

        q = (f"""
            INSERT INTO {config.MARIA_TABLE}
            (tmeas,device_id,sensor_name,sensor_value)
            VALUES (?,?,?,?)
        """
        )
        cur = conn.cursor()
        try:
            cur.executemany(q,data)
            result = True
        except Exception as e:
            log.error(e)
        cur.close()
        conn.commit()
        conn.close()

        if result:
            log.info(f'Deleting {row_ids} from sync table')
            q = "DELETE FROM sensorDataSyncMaria WHERE ROWID=?"
            db.executemany(q,row_ids)
        else:
            log.error('Writing to mariaDB failed')