var app = require('http').createServer(),
    io = require('socket.io').listen(app),
    logger  = io.log,
    redis = require('redis').createClient();

app.listen(8080);

io.configure(function() {
    io.set('close timeout', 60*60*24); // 24h
});

redis.psubscribe('session_*');

io.sockets.on('connection', function(socket) {
    console.log('conn to io');
    redis.on('pmessage', function(pattern, channel, message) {
        console.log('new message on session, channel:' + channel + ' message: ' + message);
        socket.emit(channel, message);
    });

    socket.on('disconnect', function () {
        console.log("Socket disconnected");
    }); 
});

// io.sockets.on('connection', function (socket) {
//   io.sockets.emit('this', { will: 'be received by everyone'});

//   socket.on('private message', function (from, msg) {
//     console.log('I received a private message by ', from, ' saying ', msg);
//   });

//   socket.on('disconnect', function () {
//     io.sockets.emit('user disconnected');
//   });
// });
