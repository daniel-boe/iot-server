import tomllib as toml
from loguru import logger as log
from dataclasses import dataclass, field
from pathlib import Path

def load_config():
    try:
        return RootConfig(**toml.loads(Path('config.toml').read_text()))
    except FileNotFoundError:
        return RootConfig()
    except toml.TOMLDecodeError:
        return RootConfig()
    
def validate_nested_class(obj:object,
                          hint:type,
                          name:str):
    if not isinstance(obj,(dict,hint)):
        raise ValueError(f'{name} is invalid must be dict or {hint.__name__}')
    elif isinstance(obj,dict):
        log.debug(f'Data passed for {name}, validating...')
        return hint(**obj)
    else:
        log.debug(f'No data passed, returning default object')
        return obj

@dataclass
class LocalDBConfig:
    name: str = 'db.sqlite'
    schema: str = 'schema.sql'
    handlers_dir: str = '.DataHandlers'

@dataclass
class RootConfig:
    local_db: LocalDBConfig = field(default_factory=LocalDBConfig)
    remote_db: dict[str,dict] = field(default_factory=dict) 

    def __post_init__(self):
        for attr in ['local_db',]:
            res = validate_nested_class(
                self.__getattribute__(attr),
                self.__annotations__.get(attr),
                attr
            )
            self.__setattr__(attr,res)