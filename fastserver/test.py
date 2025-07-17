import httpx
import random
import time

url = 'http://localhost:8000/sensor-record/'
device_id = 'ttt123456789ttt'

for i in range(10):
    measurement='test'
    tags = dict(id=device_id,location='bedroom')
    fields = [dict(name='temperature',value=random.randint(10,20)+random.random(),dtype='float'),
            dict(name='humidity',value=random.randint(45,65)+random.random(),dtype='float'),
            dict(name='relay_state',value=random.choice([True,False]),dtype='bool')]
    packet = dict(measurement=measurement,tags=tags,fields=fields)
    with httpx.Client() as client:
        response = client.post(url=url,json=packet)
#     response = requests.post(url,json=packet)
    print(f'status code:{response.status_code}')
    time.sleep(1)