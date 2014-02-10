var app = require('http').createServer(),
    io = require('socket.io').listen(app),
    moment = require('moment'),
    _ = require('underscore');
    logger  = io.log,
    redis = require('redis');
// used when storing socket values in redis
var redisSocketPrefix = 'sockets_';
var redisSessionPrefix = 'sessions_';

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
                // TODO: bug here!
                socket.sessions.push(session.uuid);
            } else {
                console.log('create new sessions array');
                socket.sessions = [session.uuid];
            }

            // add to redis
            addSessionToUser(socket.username, session.uuid, socket.id);
        } else if (pattern == mpattern) {
            // this is message notification
            console.log('message pattern: ' + socket.username + ' id: ' + socket.id);
            var m = JSON.parse(message);
            console.log('message dir: ' + m.direction);
            if (m.direction == 'TO_ANON') {
                // update user when she send messages
                console.log('will update ' + m.session.target.username);
                // TODO: find a better way to handle this!!
                updateUserRank(m.session.target.username);
            }
        }

        socket.emit(channel, message);
    });

    socket.on('disconnect', function () {
        var i = all_sockets.indexOf(socket);
        console.log("Socket disconnected: " + socket.id);
        console.log('User disconnected: ' + socket.username);
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

            //
            removeSocketFromUser(socket.username, socket.id);

            if (!has_sockets) {
                console.log('no sockets remaining for user ' + socket.username + " delete all sessions");
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

        console.log("---after----");
        all_sockets.forEach(function(ii) {
            console.log(">>> socket.username: " + ii.username);
            ii.sessions.forEach(function(session) {
                console.log(">>>   " + session);
            });
        });
        console.log("---after----");
    });

    socket.on('active_connection', function(data) {
        if (data.username) {
            socket.username = data.username;
            console.log('new user: ' + data.username);
            // TODO: maybe merge here??
            updateUserRank(data.username);
            // add new socket to redis
            addSocketToUser(data.username, socket.id);
        } else {
            console.log('no username in hear');
        }
    });
});


function updateUserRank(username) {
    // score is current date
    var score = parseInt(moment().format('YYMMDDHHmm'));
    var args = ["active_connections", score, username];
    var multi = updater.multi();
    multi.zadd(args);
    multi.exec(function(err, response) {
        if (err) throw err;
        console.log(response);
    });
};


function addSocketToUser(username, socket__id) {
    if (username) {
        updater.sadd(redisSocketPrefix + username, socket__id);
    } else {
        throw('no username....');
    }
};

function addSessionToUser(username, session__uuid, socket__id) {
    var socket_args = [redisSocketPrefix + username, socket__id];
    var session_args = [redisSessionPrefix + username, session__uuid];
    var multi = updater.multi();
    // multi.sadd(socket_args);
    multi.sadd(session_args);
    multi.exec(function(err, response) {
        if (err) throw err;
    });
};


function removeSessionFromSocketSessions(socket, session__uuid) {
    var k = socket.sessions.indexOf(session__uuid);
    socket.sessions.splice(k, 1);
    // // remove from redis as well
    var username = socket.username;
    if (username) {
        updater.srem(redisSessionPrefix + username, session__uuid);
    } else {
        throw('username not set for this socket while operation on redis');
    }
};

function removeSocketFromUser(username, socket__id) {
    console.log('removeSocketFromUser: ' + username + " id: " + socket__id);
    // remove this socket from redis
    updater.srem(redisSocketPrefix + username, socket__id);
    // if there are no sockets left for this user, then
    // delete all sessions and sockets
    updater.scard(redisSocketPrefix + username, function(err, count) {
        if (err) throw err;
        console.log(count + " number of sockets for " + username);

        if (count == 0) {
            console.log('deleting all for ' + username);
            var multi = updater.multi();
            multi.del(redisSocketPrefix + username);
            multi.del(redisSessionPrefix + username);
            multi.exec(function(err, response) {
                if (err) throw err;
            });
        }
    });

    debugNodeSockets();
};



function debugNodeSockets() {
    console.log("---before----");
    all_sockets.forEach(function(ii) {
        console.log(">>> socket.username: " + ii.username);
        ii.sessions.forEach(function(session) {
            console.log(">>>   " + session);
        });
    });
    console.log("---before----");
};
