from fastapi import FastAPI, BackgroundTasks, Depends
from fastserver import models
from devtools import debug
from fastserver import tasks
from fastserver.database import get_db

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.post("/sensor-data/")
async def sensor_data(packet: models.RawDeviceRecord, db: Depends(get_db), background_tasks: BackgroundTasks,):
    # debug(packet)
    tasks.insert_data_to_local(packet)
    # background_tasks.add_task(tasks.handle_influx)
    return {"status": "Hello World"}

@app.post("/sensor-data-many/")
async def sensor_data_many(packet: models.RawDeviceRecordMany, background_tasks: BackgroundTasks):
    tasks.insert_data_to_local(packet)
    # background_tasks.add_task(tasks.handle_influx)
    return {"status": "Hello World"}