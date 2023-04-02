import sqlite3
from threading import Lock
from fastserver.config import DB_LOC, DB_SCHEMA
from loguru import logger as log

def init_db():
    with sqlite3.connect(DB_LOC) as db:
        db.executescript(DB_SCHEMA.read_text())
    db.close()

def get_db():
    db = DB_Session()
    try:
        yield db
    finally:
        db.close()

class DB_Session:

    def __init__(self) -> None:
        self.db = sqlite3.connect(DB_LOC)

class DB_Manager:
    db_lock = Lock()
    def __init__(self) -> None:
        self.db = sqlite3.connect(DB_LOC)
        self.db.close()
        init_db()

    def get_data_many(self,q):
        with self.db_lock:
            data = self.get_db().execute(q).fetchall()
            self.close_db()
        return data

    def get_data_one(self,q):
        with self.db_lock:
            data = self.get_db().execute(q).fetchone()
            self.close_db()
        return data
    
    def execute_many(self,q,data):
        with self.db_lock:
            self.get_db().executemany(q,data)
            self.close_db()

    def execute_single(self,q,data):
        with self.db_lock:
            self.get_db().execute(q,data)
            self.close_db()
        

    def get_db(self):
        if not self.is_open():
            log.info('Opening DB connection')
            self.db = sqlite3.connect(DB_LOC,check_same_thread=False)
            self.db.row_factory=sqlite3.Row
        return self.db

    def is_open(self):
        try:
            cur = self.db.cursor()
            log.info('Database connection is open')
            cur.close()
            return True
        except sqlite3.ProgrammingError:
            log.info('Database is closed')
            return False 

    def close_db(self,commit = True):
        if not self.is_open():
            log.info('database is already closed')
            return True
        if commit:
            self.db.commit()
        self.db.close()
        return True

    