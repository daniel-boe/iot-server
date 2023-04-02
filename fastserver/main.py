from fastapi import FastAPI, BackgroundTasks, Depends
from fastserver import models
from devtools import debug
from fastserver import tasks
from fastserver.database import get_db, insert_data_to_local, init_db
from sqlite3 import Connection

init_db()
remote_data_manager = tasks.RemoteDBManager()
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/sensor-data/")
async def sensor_data(packet: models.RawDeviceRecord, background_tasks: BackgroundTasks, db: Connection=Depends(get_db)):
    # debug(packet)
    insert_data_to_local(db,packet)
    background_tasks.add_task(remote_data_manager.handle_data)
    return {"status": "Hello World"}

@app.post("/sensor-data-many/")
async def sensor_data_many(packet: models.RawDeviceRecordMany, background_tasks: BackgroundTasks, db: Connection=Depends(get_db)):
    insert_data_to_local(db,packet)
    background_tasks.add_task(remote_data_manager.handle_data)
    return {"status": "Hello World"}