import datetime as dt
import json
from enum import StrEnum
from pydantic import BaseModel, Field as PyField, TypeAdapter,ConfigDict, field_validator

def utc_time(no_tz=True):
    tz=dt.timezone.utc
    if no_tz:
        return dt.datetime.now(tz).replace(tzinfo=None)
    else:
        return dt.datetime.now(tz)     

class FieldTypes(StrEnum):
    STRING = 'string'
    FLOAT = 'float'
    INT = 'int'
    BOOL = 'bool'

class Field(BaseModel):
    name: str
    value: None|str|float|int|bool
    dtype: FieldTypes

    def format_line_protocol(self):
        if self.value is None: raise ValueError('Line Protocol cannot have null values')
        match self.dtype:
            case FieldTypes.STRING:
                return f'{self.name}="{self.value}"'
            case FieldTypes.FLOAT:
                return f'{self.name}={self.value}'                
            case FieldTypes.INT:
                return f'{self.name}={int(self.value)}i'
            case FieldTypes.BOOL:
                return f'{self.name}={bool(self.value)}'
            case _:
                return f'{self.name}={self.value}'

class Tags(BaseModel):
    id: str
    __pydantic_extra__: dict[str,str]
    model_config = ConfigDict(extra='allow')

class Record(BaseModel):
    measurement: str
    tags:Tags
    fields:list[Field]
    time: dt.datetime = PyField(default_factory=lambda: dt.datetime.now(tz=dt.timezone.utc).replace(tzinfo=None))
    rowid: int|None = PyField(default=None, exclude=True)

    @field_validator('tags','fields',mode='before')
    @classmethod
    def load_json_strings(cls, value:str):
        if isinstance(value,str):
            return json.loads(value)
        else: return value

    def model_dump_sqlite(self):
        """Records are nominally stored as rows in a sqlite db.
        tags and fields are stored as sqlite JSON strings.  To write to the 
        sqlite db, we need a dictionary where tags and fields are JSON strings. 
        To accomplish this, we need a custom model dump that effectively combines
        the root model_dump and mdoel_dump_json
        """
        return dict(
            measurement = self.measurement,
            tags = self.tags.model_dump_json(),
            fields = json.dumps([f.model_dump() for f in self.fields]),
            time = self.time.isoformat()
        )
    def model_dump_line_protocol(self) -> str:

        time = int(self.time.timestamp()*1000) 
        tags = ','+','.join([f'{k}={v}' for k,v in self.tags.model_dump().items()]) if self.tags else ''
        fields = ','.join([f.format_line_protocol() for f in self.fields if f.value is not None])
        return f"{self.measurement}{tags} {fields} {time}"    

class RawDeviceRecord(BaseModel):
    device_id: str
    tmeas: dt.datetime = PyField(default_factory=utc_time) 
    measurements: dict

    class Config: 
        json_schema_extra = {
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
        json_schema_extra = {
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
        json_schema_extra = {
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
        json_schema_extra = {
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
            fields = dict(sensor_value=self.sensor_value,tcreate=now.timestamp())
        )
    
    def to_sql(self):
        return (self.tmeas,self.device_id,self.sensor_name,self.sensor_value)
    
# Define some adaptors for lists of each model
TableRecordList = TypeAdapter(list[TableRecord])