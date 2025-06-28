const latest_records_table = document.getElementById('latest-records-table');
latest_records_table.addEventListener('click',tableSelectRow)

window.addEventListener('load',getLatestRecords);

async function getLatestRecords(event) {
    clearTable();

    const url = "/last-measurements/";
    const response = await fetch(url);
    const jsonData = await response.json();
    if (jsonData['results'].length) {
        populateTable(jsonData['results']);
    }
    else {
        alert('No Results Found')
    }
    
}

function populateTable(data) {
    console.log(data);
    data.forEach(record => {
        let row = latest_records_table.getElementsByTagName('tbody')[0].insertRow();
        row.id = `record-${record['device_id']}`;

        let deviceCell = row.insertCell();
        deviceCell.innerHTML = `${record['device_id']}`;

        let timeCell = row.insertCell();
        timeCell.innerHTML = record['seconds_ago'];

        let sensorCell = row.insertCell();
        sensorCell.innerHTML = record['sensor_name'];

        let valueCell = row.insertCell();
        valueCell.innerHTML = record['value'];
    });
}


function clearTable() {
    console.log('Clearing Table');
    n_rows = latest_records_table.rows.length
    for (let index = 1; index < n_rows; index++) {
        latest_records_table.deleteRow(-1);
    }
}

function tableSelectRow(event) {
    console.log('Table was clicked');
    // TODO - link to time chart for this senssor 
}