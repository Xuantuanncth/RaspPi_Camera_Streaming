var express = require('express');
var router = express.Router();
const fs = require('fs');
const { runInContext } = require('vm');
const socket_api = require('../socket_api');
const videoFolder = '/home/pi/camera_detect/camera_streaming/video_record';
const datasetPath = '/home/pi/camera_detect/camera_streaming/dataset';
/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index',{title: 'Home'});
});

router.get('/streaming', function(req, res, next) {
    socket_api.streamMode("ON");
    res.render('streaming',{title: 'Streaming'});
})

router.get('/recording', function(req, res, next) {
    socket_api.streamMode("OFF");
    res.render('recording',{title: 'Recording'});
})
router.get('/setting', function(req, res, next) {
    res.render('setting',{title: 'Setting'});
})

router.post('/login', function(req, res) {
    const {username, password} = req.body;

    if(!username || !password){
        return res.status(400).json({error:"Invalid username or password"});
    }

    if(username == "admin" && password == "123"){
        res.redirect('/streaming');
    } else {
        return res.status(400).json({error:"Invalid username or password"});
    }
})

router.get('/video/:name', function(req, res) {
    const videoDefault = "WIN_20231118_16_15_59_Pro.mp4";
    const videoName = req.params.name;
    console.log("Video: ",videoName);
    const videoPath = videoFolder+"/"+videoName;
    // if(videoName){
    //     videoPath = folderPath+"/"+videoName;
    // } else {
    //     videoPath = folderPath+"/"+videoDefault;
    // }
    console.log("Video path: ",videoPath);
    const range = req.headers.range 
    const videoSize = fs.statSync(videoPath).size 
    const chunkSize = 1 * 1e6; 
    const start = Number(range.replace(/\D/g, ""));
    const end = Math.min(start + chunkSize, videoSize - 1) 
    const contentLength = end - start + 1; 
    const headers = { 
        "Content-Range": `bytes ${start}-${end}/${videoSize}`, 
        "Accept-Ranges": "bytes", 
        "Content-Length": contentLength, 
        "Content-Type": "video/mp4"
    } 
    res.writeHead(206, headers) 
    const stream = fs.createReadStream(videoPath, { 
        start, 
        end 
    }) 
    stream.pipe(res) 
})

router.get('/listVideo', function(req, res) {
    console.log("Show list video");
    fs.readdir(videoFolder, (err, files) => {
            if (err) {
                console.error('Error reading folder:', err);
                return res.status(400).json({error:err});;
            }
        
            console.log('Files in the folder:');
            files.forEach(file => {
                console.log(file);
            });
            return res.status(200).send(files);
        }
    )
        
    }
)

router.get('/takePicture', function(req, res) {
    console.log("Take picture");
    socket_api.takePicture();
    res.status(200).json({success:true});
});

router.get('/trainModel', function(req, res) {
    console.log("Train model");
    socket_api.trainModel();
    res.status(200).json({success:true});
});
router.get('/settingTimes/startTime=:startTime&stopTime=:stopTime', function(req, res) {
    const startTime = req.params.startTime;
    const stopTime = req.params.stopTime;
    console.log('StartTime: ',startTime,": stopTime: ",stopTime);
    socket_api.sendSettingTime(startTime,stopTime);
    res.status(200).json({success:true});
});

router.get('/settingOwner/name=:name&email=:email', function(req, res) {
    const name = req.params.name;
    const email = req.params.email;
    console.log('name: ',name,": email: ",email);
    var newMemberPath = datasetPath+"/"+name;
    fs.mkdir(newMemberPath, { recursive: true }, (err) => {
        if (err) {
            console.error(`Error creating folder: ${err.message}`);
        } else {
            console.log(`Folder "${newMemberPath}" created successfully.`);
        }
    });
    socket_api.sendSettingOwner(name,email);
    res.status(200).json({success:true});
});


module.exports = router;
