# iot-server

## Depenencies
```pip install flask waitress```

1. From the _iot-server_ directory, run  ```flask --app server init-db```
    * Initialize the sqlite database (see ```db.init_db_command```)
2. To run the server in debug mode, execute ```flask --app server --debug run --host 0.0.0.0``` from the _iot-server_ directory.
    * This spins up a test server [here](http://127.0.0.1:5000)
3. Test the api by entering this command into a bash shell (for some reason, powershell encodes the data weird, so use bash instead):  
    ```
    curl -X POST http://127.0.0.1:5000/api/sensor-data -H "Content-Type: application/json" -d '{"sensor_data": {"temp": 13.48471, "humidity": 46.39872}, "host": "test-data"}'
    ```
4.  Connect to the app's database (_~/instance/senserver.sqlite_) to verify data showed up
