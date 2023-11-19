const linkVideo = "http://localhost:3000/video/"

window.onload = function loadData() {
    console.log("[loadData]");
    const url = "/listVideo";
    fetch(url).then((response) => {
        response.json().then((data) => {
            if (data.error) {
                console.log("Data error: ", data.error);
            } else {
                createListVideo(data);
            }
        })
    })
}

function createListVideo(data) {
    console.log("[createListVideo]");
    const listVideo = document.getElementById("list-video");
    data.forEach(element => {
        console.log("Element: ", element);
        let div = createTagVideo(element);
        listVideo.appendChild(div);
    });
}

function createTagVideo(data){
    let playVideo = document.getElementById("video-display");
    const videoLabel = document.getElementById("video_label");
    let li = document.createElement("h3");
    li.innerHTML=data;
    li.id="li-data";
    li.classList = "text-blue-500 hover:text-red-500 text-sm pt-[20px]"
    li.onclick = function() {
        playVideo.src = linkVideo + data;
        videoLabel.innerHTML=data
    }
    return li;
}

function record_mode() {
    console.log('record_mode');
    const stream_button = document.getElementById('steams-button');
    const recording_button = document.getElementById('record-button');
    stream_button.style.backgroundColor="#FCFCFC";
    recording_button.style.backgroundColor="#6CD2E9"
}

function stream_mode() {
    console.log('record_mode');
    const stream_button = document.getElementById('steams-button');
    const recording_button = document.getElementById('record-button');
    recording_button.style.backgroundColor="#FCFCFC";
    stream_button.style.backgroundColor="#6CD2E9"
}

function sendConfigTime(){
    let startTime = document.getElementById('start_time');
    let stopTime = document.getElementById('stop_time');
    let url = "/settingTimes/startTime="+startTime.value+"&stopTime="+stopTime.value;
    fetch(url).then((response) => {
        response.json().then((data) => {
            if (data.error) {
                console.log("Data error: ", data.error);
            } else {
                console.log(data);
            }
        })
    })
}

