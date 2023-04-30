-- DROP TABLE IF EXISTS sensorData;

-- Data Log Table  
CREATE TABLE IF NOT EXISTS sensorData (
  rowid INTEGER PRIMARY KEY AUTOINCREMENT,
  device_id TEXT NOT NULL,
  tmeas TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  sensor_name TEXT NOT NULL,
  sensor_value FLOAT
);

-- Data Log Table queue for shipping data to remote 
CREATE TABLE IF NOT EXISTS sensorDataSync (
  rowid INTEGER PRIMARY KEY AUTOINCREMENT,
  device_id TEXT NOT NULL,
  tmeas TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL,
  sensor_name TEXT NOT NULL,
  sensor_value FLOAT
);

-- experiment log - 
CREATE TABLE IF NOT EXISTS experimentData (
  device_id TEXT NOT NULL,
  uut_id TEXT NOT NULL,
  test_id TEXT NOT NULL,
  tmeas TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP 
);

CREATE TRIGGER IF NOT EXISTS remoteQueueTrigger
    AFTER INSERT ON sensorData
    BEGIN
    INSERT INTO sensorDataSync (device_id, tmeas, created_at, sensor_name, sensor_value)
        VALUES (new.device_id, new.tmeas, new.created_at, new.sensor_name, new.sensor_value);
    END;
