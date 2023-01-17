import json
from time import time
from flask import Blueprint
from flask import render_template
from flask import request
from . import db

bp = Blueprint('api', __name__,url_prefix = '/api')

@bp.route('/data',methods=['GET','POST'])
def post_temperature_data():
    """
    Legacy endpoint - remains here for comptatability purposes - do not use.  
    """
    print('API here - ')
    if request.method=='POST':
        if request.is_json:
            dat = json.loads(request.get_json())
            db.handle_temp_humid_json(dat)
        else:
            print('No Data Posted')
    else:
        print('GET Request, nothing to do here')
    return render_template('index.html')



@bp.route('/sensor-data',methods=['GET','POST'])
def post_sensor_data():
    """
    Endpopint for handling generic sensor data. Incoming json should follow this pattern:
    
        {'host':<IoT device host name>,'sensor_data':{<field-1>:<value>,<field-2>:value ...}}

    Here is an example of some real data from a temperature/humdity sensor:
        {"host": "test-data","sensor_data": {"temp": 13.48471,"humidity":46.39872}}}

    Note that it is not required to include measurement timestamp in the incoming json. Many IoT
    devices will not have a real time clock, so a timestamp will always be added here unless one is 
    included in the json.

    """
    print('API here - ')
    if request.method=='POST':
        print(request.is_json)
        if request.is_json:
            try:
                dat = json.loads(request.get_json())
            except TypeError:
                dat = request.get_json()
            if 'tmeas' not in dat:
                dat.update({'tmeas':int(time())})
            db.handle_sensor_json(dat)
        else:
            print('No Data Posted')
    else:
        print('GET Request, nothing to do here')
    return render_template('index.html')
