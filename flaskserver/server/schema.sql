DROP TABLE IF EXISTS indigoSerialNums;
DROP TABLE IF EXISTS actionLog;
DROP TABLE IF EXISTS serialNumberParams;
DROP TABLE IF EXISTS indigoSerialSync;

-- Data Log Table - username, create time, body, indigo_id, form_type 
CREATE TABLE sensorData (
  tmeas TIMESTAMP NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  host TEXT NOT NULL,
  sensor_name TEXT NOT NULL,
  sensor_value FLOAT
);
