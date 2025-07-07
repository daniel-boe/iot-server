import datetime as dt
from pydantic import BaseModel, Field, type_adapter

def utc_time(no_tz=True):
    tz=dt.timezone.utc
    if no_tz:
        return dt.datetime.now(tz).replace(tzinfo=None)
    else:
        return dt.datetime.now(tz)     

class RawDeviceRecord(BaseModel):
    device_id: str
    tmeas: dt.datetime = Field(default_factory=utc_time) 
    measurements: dict

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
    tmeas: dt.datetime
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
    tmeas: dt.datetime  
    created_at: dt.datetime
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

    def to_influx(self,measurement):
        now = utc_time()
        return dict(
            measurement = measurement,
            tags = dict(device_id=self.device_id,sensor_name=self.sensor_name),
            time = self.tmeas.isoformat(timespec='milliseconds'),
            fields = dict(sensor_value=self.sensor_value,tcreate=now)
        )
    
    def to_sql(self):
        return (self.tmeas,self.device_id,self.sensor_name,self.sensor_value)
    
# Define some adaptors for lists of each model
TableRecordList = type_adapter(list[TableRecord])