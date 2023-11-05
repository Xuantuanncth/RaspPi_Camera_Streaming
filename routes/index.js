var express = require('express');
var router = express.Router();
const fs = require('fs');

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

router.get('/video', function(req, res) {
    const range = req.headers.range 
    const videoPath = 'public/videos/test_video.mp4'; 
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

module.exports = router;
