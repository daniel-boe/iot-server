-- DROP TABLE IF EXISTS sensorData;

-- Data Log Table  
CREATE TABLE IF NOT EXISTS sensorData (
  device_id TEXT NOT NULL,
  tmeas TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  sensor_name TEXT NOT NULL,
  sensor_value FLOAT
);

-- Data Log Table queue for shipping data to remote 
CREATE TABLE IF NOT EXISTS sensorDataSyncInflux (
  device_id TEXT NOT NULL,
  tmeas TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL,
  sensor_name TEXT NOT NULL,
  sensor_value FLOAT
);

-- Data Log Table queue for shipping data to remote 
CREATE TABLE IF NOT EXISTS sensorDataSyncMaria (
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

CREATE TRIGGER IF NOT EXISTS influxQueueTrigger
    AFTER INSERT ON sensorData
    BEGIN
    INSERT INTO sensorDataSyncInflux (device_id, tmeas, created_at, sensor_name, sensor_value)
        VALUES (new.device_id, new.tmeas, new.created_at, new.sensor_name, new.sensor_value);
    END;

CREATE TRIGGER IF NOT EXISTS mariaQueueTrigger
    AFTER INSERT ON sensorData
    BEGIN
    INSERT INTO sensorDataSyncMaria (device_id, tmeas, created_at, sensor_name, sensor_value)
        VALUES (new.device_id, new.tmeas, new.created_at, new.sensor_name, new.sensor_value);
    END