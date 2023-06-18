const logger_selector = document.getElementById('logger-select');

window.addEventListener('load',populateLoggerList);
logger_selector.addEventListener('change',update_chart);

let dataChart = new Chart(document.getElementById('myChart'), {
    type: 'line',
    data: {
      datasets: [{
        data: [],
        borderWidth: 1
      }]
    },
    options: {
      scales: {
        xAxes: {
            type: 'time',
            time:{
                    minUnit: 'second'
                }
          }
      }
    }
  });


function addData(chart, xyvals) {
    chart.data.datasets.forEach((dataset) => {
        dataset.data.push(xyvals);
    });
    chart.update();
}

function removeData(chart) {
    chart.data.datasets.forEach((dataset) => {
        dataset.data.pop();
    });
    chart.update();
}

async function update_chart(){
    let data = await get_data();
    dataChart.data.datasets = [];
    dataChart.update();

    let sensors = data.results.map(row => row.sensor_name);
    sensors = [... new Set(sensors)];
    
    let subset = [];
    let xy = [];
    
    sensors.forEach(function(sensor) {
        subset = data.results.filter(row => row.sensor_name == sensor);
        xy = subset.map(row => ({x:row.tmeas,y:row.sensor_value}));
        console.log(sensor)
        console.log(xy)
        dataChart.data.datasets.push({label:sensor, data: xy});
    })

    dataChart.update();
}

async function get_data() {
    const logger = logger_selector.value;
    console.log(logger);
    const params = {device_id:logger,seconds_ago:172800};
    const url = "/seconds-ago?" + new URLSearchParams(params);
    const response = await fetch(url);
    const jsonData = await response.json();
    return jsonData;
}

async function populateLoggerList(){
    const response = await fetch('/device-ids/',{
        method:"GET"
    });
    let data = await response.json();
    console.log(data);
    data.results.forEach(function(item) {
        const myElement = new Option(`${item["device_id"]}`,`${item["device_id"]}`);
        logger_selector.add(myElement);
    })
}