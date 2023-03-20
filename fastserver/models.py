from datetime import datetime
from pydantic import BaseModel, validator
from fastserver.config import INFLUX_MEASUREMENT


class RawDeviceRecord(BaseModel):
    device_id: str
    tmeas: datetime = None 
    measurements: dict

    @validator('tmeas', pre=True, always=True)
    # Dynamic defaults (keep an eye here https://github.com/pydantic/pydantic/issues/866)
    def set_ts_now(cls, v):
        return v or datetime.utcnow()

    class Config: 
        schema_extra = {
            "example":{
                "device_id":"12345abcde",
                "measurements":{
                    "temperature_1":23.4,
                    "temperature_2":23.9,
                    "humidity":54.3
                }
            }
        }


class RawSample(BaseModel):
    tmeas: datetime
    measurements: dict

    class Config: 
        schema_extra = {
            "example":{
                "tmeas":'2023-01-26 15:00:00',
                "measurements":{
                    "temperature_1":23.4,
                    "temperature_2":23.9,
                    "humidity":54.3
                }
            }
        }

class RawDeviceRecordMany(BaseModel):
    device_id: str
    samples: list[RawSample]

    class Config: 
        schema_extra = {
            "example":{
                "device_id":"12345abcde",
                "samples":[
                    {"tmeas":'2023-01-26 15:00:00',
                    "measurements":{
                        "temperature_1":23.4,
                        "temperature_2":23.9,
                        "humidity":54.3
                        }
                    },
                    {"tmeas":'2023-01-26 15:00:10',
                    "measurements":{
                        "temperature_1":23.9,
                        "temperature_2":24.6,
                        "humidity":54.8
                        }
                    }

                ]
            }
        }

class TableRecord(BaseModel):
    rowid: int
    device_id: str
    tmeas: datetime  
    created_at: datetime
    sensor_name: str
    sensor_value: float

    class Config: 
        schema_extra = {
            "example":{
                "device_id":"12345abcde",
                "tmeas":'2023-01-26 15:00:00',
                "created_at":'2023-01-26 15:00:01',
                "sensor_name":'humidity',
                "sensor_value":54.3
            }
        }

    def to_influx(self):
        return dict(
            measurement = INFLUX_MEASUREMENT,
            tags = dict(device_id=self.device_id,sensor_name=self.sensor_name),
            time = self.tmeas.isoformat(timespec='milliseconds'),
            fields = dict(sensor_value=self.sensor_value,tcreate=datetime.utcnow().isoformat(timespec='milliseconds'))
        )