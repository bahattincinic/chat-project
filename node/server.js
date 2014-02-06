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
var mpattern = "message_*";
subscriber.psubscribe(mpattern);
updater = redis.createClient();

var all_sockets = [];
io.sockets.on('connection', function(socket) {
    console.log('on connection');
    all_sockets.push(socket);

    subscriber.on('pmessage', function(pattern, channel, message) {
        // console.log('new message, channel:' + channel + ' pattern: ' + pattern);
        if (pattern == spattern) {
            // this is session creation
            console.log('session username:' + socket.username + ' id: ' + socket.id);
            var session = JSON.parse(message);
            console.log(session.uuid);
            if (socket.sessions) {
                console.log('add to session array');
                socket.sessions.push(session.uuid);
            } else {
                console.log('create new sessions array');
                socket.sessions = [session.uuid];
            }
//            printAllSockets();
        } else if (pattern == mpattern) {
            // this is message notification
            console.log('message pattern: ' + socket.username + ' id: ' + socket.id);
            var m = JSON.parse(message);
            console.log('message dir: ' + m.direction);
            if (m.direction == 'TO_ANON') {
                // update user when she send messages
                console.log('will update ' + m.session.target.username);
                update_user(m.session.target.username);
            }
        }

        socket.emit(channel, message);
    });

    socket.on('disconnect', function () {
        var i = all_sockets.indexOf(socket);
        console.log("Socket disconnected: " + i);
        console.log('user disconnected: ' + socket.username);
//        console.log('active sockets len now: ' + all_sockets.length);
        all_sockets.splice(i, 1); // remove element
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
//                io.sockets.emit('disconnected_' + socket.username);
                if (socket.sessions && socket.sessions.length > 0) {
                    socket.sessions.forEach(function(session) {
                        // find all sockets that has this session
                        console.log("session to be closed " + session);
                        _.filter(all_sockets, function(_socket) {
                            if (_socket.sessions  && _socket.sessions.length > 0 && _.contains(_socket.sessions, session)) {
                                _socket.emit('disconnected_' + session, {session: session});
                                removeSessionFromSocketSessions(_socket, session);
                            }
                        });
                    });
                    // remove all sessions from removed socket
                    socket.sessions.length = 0;
                }
            } else {
                console.log('remaining sockets does exists for user ' + socket.username);
            }
        }
    });

    socket.on('user_disconnected', function(data) {
        console.log("---before----");
        all_sockets.forEach(function(ii) {
            console.log(">>> socket.username: " + ii.username);
            ii.sessions.forEach(function(session) {
                console.log(">>>   " + session);
            });
        });
        console.log("---before----");
        // triggered when user herself closes session voluntarily
        console.log("disconnected: " + data.user + " session.id: " + data.uuid);
        console.log('socket id: ' + socket.id + " socket user: " + socket.username);
        if (data.uuid) {
            // find parties to inform
            var pending_notification = [];
            _.filter(all_sockets, function(i) {
                if (i.sessions && i.sessions.length > 0 &&  _.contains(i.sessions, data.uuid)) {
                    console.log('socket with session: ' + i.id);
                    pending_notification.push(i);
                }
            });

            // inform all parties
            if (pending_notification.length > 0) {
                pending_notification.forEach(function (socket) {
                    socket.emit('disconnected_' + data.uuid, data);
                    removeSessionFromSocketSessions(socket, data.uuid);
                });
            }

            // reset pending notification
            pending_notification.length = 0;
        }

        console.log("---before----");
        all_sockets.forEach(function(ii) {
            console.log(">>> socket.username: " + ii.username);
            ii.sessions.forEach(function(session) {
                console.log(">>>   " + session);
            });
        });
        console.log("---before----");
    });

    socket.on('active_connection', function(data) {
        if (data.username) {
            socket.username = data.username;
            console.log('new user: ' + data.username);
            update_user(data.username);
        } else {
            console.log('no username in hear');
        }
    });
});


function update_user(username) {
    // redis conn
    var score = parseInt(moment().format('YYMMDDHHmm'));
    var args = ["active_connections", score, username];
    var multi = updater.multi();
    multi.zadd(args);
    multi.exec(function(err, response) {
        if (err) throw err;
        console.log(response);
    });
}

function printAllSockets() {
    console.log('print all sockets');
    all_sockets.forEach(function(socket) {
        console.dir(socket);
    });
}

function removeSessionFromSocketSessions(socket, session_uuid) {
    var k = socket.sessions.indexOf(session_uuid);
    socket.sessions.splice(k, 1);
}