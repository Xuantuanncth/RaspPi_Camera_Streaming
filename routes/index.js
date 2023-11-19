var express = require('express');
var router = express.Router();
const fs = require('fs');
const { runInContext } = require('vm');

const folderPath = 'D:/Working/NodeJS/VideoTest';
/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('index',{title: 'Home'});
});

router.get('/homepage', function(req, res, next) {
    res.render('homepage',{title: 'Home'});
})

router.post('/login', function(req, res) {
    const {username, password} = req.body;

    if(!username || !password){
        return res.status(400).json({error:"Invalid username or password"});
    }

    if(username == "admin" && password == "123"){
        res.redirect('/homepage');
    } else {
        return res.status(400).json({error:"Invalid username or password"});
    }
})

router.get('/video/:name', function(req, res) {
    const videoDefault = "WIN_20231118_16_15_59_Pro.mp4";
    const videoName = req.params.name;
    console.log("Video: ",videoName);
    const videoPath = folderPath+"/"+videoName;
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
        fs.readdir(folderPath, (err, files) => {
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

router.get('/settingTimes/startTime=:startTime&stopTime=:stopTime', function(req, res) {
    const startTime = req.params.startTime;
    const stopTime = req.params.stopTime;
    console.log('StartTime: ',startTime,": stopTime: ",stopTime);
    res.send("okay");
});


module.exports = router;
