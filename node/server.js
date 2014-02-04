var app = require('http').createServer(),
    io = require('socket.io').listen(app),
    moment = require('moment'),
    _ = require('underscore');
    logger  = io.log,
    redis = require('redis');

app.listen(8080);

io.configure(function() {
    io.set('close timeout', 60*60*24); // 24h
    io.set('log level', 1);
});

subscriber = redis.createClient();
var spattern = "session_*";
subscriber.psubscribe(spattern);
// var mpattern = "message_*";
// subscriber.psubscribe(mpattern);
updater = redis.createClient();

var all_sockets = [];
io.sockets.on('connection', function(socket) {
    all_sockets.push(socket);
    console.log('active sockets len now: ' + all_sockets.length);

    subscriber.on('pmessage', function(pattern, channel, message) {
        console.log('new message, channel:' + channel + ' pattern: ' + pattern);
        // if (pattern == spattern) {
        //     console.log('sess pattern');
        //     // socket.join(channel);
        //     socket.emit(channel, message);
        // } else {
        //     var room_n = "session_" + channel.slice(8);
        //     console.log('m pattern: ' + room_n);
        //     // io.sockets.in(room_n).emit('message', message);
        //     socket.broadcast.to(room_n).emit('message', data)
        // }
        socket.emit(channel, message);
        // socket.emit('room', channel);
    });

    socket.on('disconnect', function () {
        var i = all_sockets.indexOf(socket);
        console.log("Socket disconnected: " + i);
        console.log('user disconnected: ' + socket.username);
        all_sockets.splice(i, 1); // remove element
        console.log('active sockets len now: ' + all_sockets.length);
        // search for socket username
        if (socket.username) {
            // any client left for this user?
            var has_sockets = false;
            _.filter(all_sockets, function(i) {
                if (i.username == socket.username) {
                    has_sockets = true;
                }
            });

            if (!has_sockets) {
                console.log('no sockets remaining for user ' + socket.username + " delete all sessions");
                // remove from redis as well
                updater.del('sessions_' + socket.username);
                // inform all users and anon that this user really disconnected
                io.sockets.emit('disconnected_' + socket.username);
            } else {
                console.log('remaining sockets exists for user ' + socket.username);
            }
        }
    });

    socket.on('active_connection', function(data) {
        if (data.username) {
            socket.username = data.username;
            console.log('new user: ' + data.username);
            // redis conn
            var score = parseInt(moment().format('YYMMDDHHmm'));
            var args = ["active_connections", score, socket.username];
            var multi = updater.multi();
            multi.zadd(args);
            multi.exec(function(err, response) {
                if (err) throw err;
                console.log(response);
            });
        } else {
            console.log('no username in hear');
        }
    });
});
