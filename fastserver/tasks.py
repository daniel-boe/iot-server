import abc
import models
from database import get_db_ctx
from pathlib import Path
from loguru import logger as log
from sqlite3 import Connection
from config import load_config
from utils import get_latest_rn

config = load_config()


for k,d in config.remote_db.items():
    match(k):
        case 'influxdb':
            from influxdb import InfluxDBClient
        case 'mariadb':
            import mariadb
        case _:
            pass



class RemoteDBManager:

    def __init__(self):
        self.handlers = self.register_handlers()

    def handle_data(self,*args,**kwargs):
        log.debug('Handling data plugins')
        for handler in self.handlers:
            with get_db_ctx() as db:
                handler.handle(db)    
        log.debug('Handling Data Plugins complete')

    def register_handlers(self):
        handlers = []
        for k,d in config.remote_db.items():

            match(k):
                case 'influxdb':
                    handlers += [InfluxHandler(**creds) for name,creds in d.items()]
                case 'mariadb':
                    handlers += [MariaHandler(**creds) for name,creds in d.items()]
                case _:
                    pass
        return handlers

class RemoteDBHandler:

    def __init__(self,**kwargs):
        self.sent_path = Path(config.local_db.handlers_dir) / Path(f'{self.__class__.__name__}.txt')
        if not self.sent_path.exists():
            with get_db_ctx() as db:
                idx=get_latest_rn(db)
            self.sent_path.write_text(f'{idx}')
            
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

    def __init__(self,
                 host:str,
                 user:str,
                 password:str,
                 database:str,
                 measurement:str,
                 port:int=8086,
                 **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.username = user
        self.password = password
        self.database = database
        self.measurement = measurement
        self.port = port

    def handler(self,db:Connection,rn):
        result = False

        log.info('Forwarding Data to InfluxDB')
        q = f'SELECT * FROM sensorDataSync WHERE rowID BETWEEN {rn} AND {rn + self.batch_limit}'
        data = db.execute(q).fetchall()
        data = [models.TableRecord(**r) for r in data]
        row_ids = [r.rowid for r in data]
        data = [r.to_influx(self.measurement) for r in data]
        log.info(f'Found {len(row_ids)} records for InfluxDB')
        
        client = InfluxDBClient(
            host = self.host,
            port = self.port,
            username = self.username,
            password = self.password,
            database = self.database
        )

        try:        
            result = client.write_points(data,time_precision='s', batch_size = 100)
        except Exception as ex:
            log.exception('Influx post failed')
        
        client.close()

        if result:
            log.info(f'Deleting {row_ids} from sync table')
            return max(row_ids)
        else:
            log.error('Writing to influx failed')

class MariaHandler(RemoteDBHandler):
    handles = 'mariadb'
    batch_limit = 10

    def __init__(self,
                 user:str,
                 password:str,
                 host:str,
                 database:str,
                 table:str,
                 port:int=3306,
                 **kwargs):
        super().__init__(**kwargs)
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = database
        self.table = table

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
            user=self.user,
            password=self.config,
            host=self.host,
            port=self.port,
            database=self.database
        )

        q = (f"""
            INSERT INTO {self.table}
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