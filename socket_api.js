const io = require( "socket.io" )();
const socket_api = {
    io: io
};

// Add your socket.io logic here!
io.on( "connection", function( socket ) {
    console.log( "A user connected" );
});

socket_api.sendSettingTime = function(start,stop){
    console.log("Setting time: " + start+   " " +   stop);
    io.emit('setting_time',{start_time:start,stop_time:stop});
}

socket_api.sendSettingOwner = function(name, email){
    console.log("sendSettingOwner: " + name+   " " +   email);
    io.emit('setting_owner',{name:name,email:email});
}

socket_api.takePicture = function(){
    console.log("takePicture");
    io.emit('take_picture',{isPicture: "true"});
}

socket_api.trainModel = function(){
    console.log("trainModel");
    io.emit('train_model',{isModel:true});
}

socket_api.streamMode = function(status){
    console.log("stream_mode");
    io.emit('stream_mode',status);
}
// end of socket.io logic

module.exports = socket_api;