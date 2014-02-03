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
        socket.emit(channel, message);
    });

    socket.on('disconnect', function () {
    });
});