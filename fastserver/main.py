import models, utils
import tasks
from fastapi import FastAPI, BackgroundTasks, Depends, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlite3 import Connection
from loguru import logger as log
from database import get_db, insert_data_to_local, init_db
from devtools import debug

init_db()
remote_data_manager = tasks.RemoteDBManager()
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

############### FRONTEND #############################


@app.get('/',response_class=HTMLResponse)
async def index(request:Request):
    return templates.TemplateResponse('index.html',{'request':request})

@app.get('/index/',response_class=RedirectResponse)
async def index_redirect(request:Request):
    return RedirectResponse('/')

@app.get('/charts/',response_class=HTMLResponse)
async def charts(request:Request):
    return templates.TemplateResponse('charts.html',{'request':request})

################### API - POSTS #######################

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

################ API - GETS ##################################

@app.get('/last-n-records/')
async def last_n_records(device_id:str|None=None, n:int=10, db:Connection=Depends(get_db)):
    log.info(f'Finding last {n} records for device: {device_id}')
    results = utils.get_data_for_id(db,device_id,n)
    if results:
        results = [r.dict(exclude = {'rowid','created_at'}) for r in results]
        return {'status':'OK','results':results}
    else:
        return {'status':'NONE','results':[]}

@app.get('/seconds-ago/')
async def records_seconds_ago(device_id: list[str] | None = Query(default=None),
                              seconds_ago:int|None=3600,
                              db:Connection=Depends(get_db)):
    log.info(f'Finding records from {device_id} last {seconds_ago/3600} hours')
    results = utils.get_recent_data(db,seconds_ago=seconds_ago,device_ids=device_id)
    if results:
        results = [r.dict(exclude = {'rowid','created_at'}) for r in results]
        return {'status':'OK','results':results}
    else:
        return {'status':'NONE','results':[]}
    
@app.get('/device-ids/')
async def device_ids(db:Connection=Depends(get_db)):
    log.info(f'Finding uniuqe device ids')
    results = utils.get_unique_devices(db)
    if results:
        results = [dict(r) for r in results]
        return {'status':'OK','results':results}
    else:
        return {'status':'NONE','results':[]}

@app.get('/last-measurements/')
async def last_measurements(db:Connection=Depends(get_db)):
    log.info(f'Finding last measurements')
    results = utils.get_last_measurements(db)
    if results:
        results = [dict(r) for r in results]
        return {'status':'OK','results':results}
    else:
        return {'status':'NONE','results':[]}