import requests
import random
import time

url='http://localhost:8000/sensor-data/'
device_id = 'ttt123456789ttt'

for i in range(10):
    measurements={'testMeas1':random.random()*40,
                'testMeas2':random.random()*40,
                'testMeas3':random.random()*20+40}
    packet = dict(device_id=device_id,measurements=measurements)
    response = requests.post(url,json=packet)
    print(f'status code:{response.status_code}')
    time.sleep(1)