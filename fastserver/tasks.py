import abc
from fastserver import models, config
from fastserver.database import get_db_ctx
from loguru import logger as log
from sqlite3 import Connection
from pathlib import Path

if 'influxdb' in config.DATA_HANDLERS:
    from influxdb import InfluxDBClient

if 'mariadb' in config.DATA_HANDLERS:
    import mariadb

class RemoteDBManager:

    def __init__(self):
        self.handlers = [c() for c in RemoteDBHandler.__subclasses__() if c.handles in config.DATA_HANDLERS]

    def handle_data(self,*args,**kwargs):
        log.debug('Handling data plugins')
        for handler in self.handlers:
            with get_db_ctx() as db:
                handler.handle(db)    
        log.debug('Handling Data Plugins complete')


class RemoteDBHandler:

    def __init__(self):
        self.sent_path = config.DB_HANDLERS_DIR / f'{self.__class__.__name__}.txt'
        if not self.sent_path.exists():
            self.sent_path.write_text('0')

    def handle(self,db:Connection):
        start_rn = int(self.sent_path.read_text())
        if new_rn := self.handler(db,start_rn):
            self.sent_path.write_text(str(new_rn + 1))

    @abc.abstractmethod
    def handler(self,db:Connection,rn:int) -> int | None:
        """
        Returns the maximum row number fetched or if None of no data were fetched
        Args:
            db (Connection): sqlite3 connection
            rn (int): row number to start fetching data from (inclusive)
        """
        pass


class InfluxHandler(RemoteDBHandler):
    handles = 'influxdb'
    batch_limit = 10

    def handler(self,db:Connection,rn):
        result = False

        log.info('Forwarding Data to InfluxDB')
        q = f'SELECT * FROM sensorDataSync WHERE rowID BETWEEN {rn} AND {rn + self.batch_limit}'
        data = db.execute(q).fetchall()
        data = [models.TableRecord(**r) for r in data]
        row_ids = [r.rowid for r in data]
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
            return max(row_ids)
        else:
            log.error('Writing to influx failed')

class MariaHandler(RemoteDBHandler):
    handles = 'mariadb'
    batch_limit = 10

    def handler(self,db:Connection,rn):
        result = False

        log.info('Forwarding Data to mariaDB')
        q = f'SELECT * FROM sensorDataSync WHERE rowID BETWEEN {rn} AND {rn + self.batch_limit}'
        data = db.execute(q).fetchall()
        data = [models.TableRecord(**r) for r in data]
        if not data:
            log.warning('No Data found to forward to maria')
            return 
        row_ids = [r.rowid for r in data]
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
            cur.close()
            conn.commit()
        except Exception as e:
            log.error(e)
        conn.close()

        if result:
            log.info(f'Data insertion to mariaDB successful')
            return max(row_ids)
        else:
            log.error('Writing to mariaDB failed')