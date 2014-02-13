var app = require('http').createServer(),
    io = require('socket.io').listen(app),
    moment = require('moment'),
    _ = require('underscore');
    logger = io.log,
    redis = require('redis');
// used when storing socket values in redis
var redisSocketPrefix = 'sockets_';
var redisSessionPrefix = 'sessions_';

app.listen(9999);


io.configure(function() {
    io.set('close timeout', 60*60*24); // 24h
    io.set('log level', 1);
});

subscriber = redis.createClient();
var spattern = "new_session";
// subscriber.psubscribe(spattern);
var mpattern = "message_*";
subscriber.psubscribe(mpattern);
updater = redis.createClient();

function Session(target, uuid, anon, anon_socket_id) {
    this.target = {'username': target};
    this.uuid = uuid;
    this.anon = {'username': anon, 'socket_id': anon_socket_id};
}

var all_sockets = [];
var all_sessions = [];
io.sockets.on('connection', function(socket) {
    console.log('on connection');
    all_sockets.push(socket);

    // subscriber.on('pmessage', function(pattern, channel, message) {
    //     // console.log('new message, channel:' + channel + ' pattern: ' + pattern);
    //     if (pattern == spattern) {
    //         // this is session creation
    //         console.log('session username:' + socket.username + ' id: ' + socket.id);
    //         // var session = JSON.parse(message);
    //         // console.log(session.uuid);
    //         // console.dir(session);
    //         if (socket.sessions) {
    //             console.log('add to session array');
    //             // TODO: bug here!
    //             socket.sessions.push(message);
    //         } else {
    //             console.log('create new sessions array');
    //             socket.sessions = [message];
    //         }

    //         startSession(message);
    //         // add to redis
    //         // addSessionToUser(socket.username, session.uuid, socket.id);
    //     } else if (pattern == mpattern) {
    //         // this is message notification
    //         console.log('message pattern: ' + socket.username + ' id: ' + socket.id);
    //         var m = JSON.parse(message);
    //         console.log('message dir: ' + m.direction);
    //         if (m.direction == 'TO_ANON') {
    //             // update user when she send messages
    //             console.log('will update ' + m.session.target.username);
    //             // TODO: find a better way to handle this!!
    //             // updateUserRank(m.session.target.username);
    //         }
    //     }

    //     // socket.emit(channel, message);
    // });

    socket.on('initiate_session', function(data) {
        console.log('initiate_session');
        console.dir(data);
        if (data.anon && data.uuid && data.target) {
            var session = new Session(data.target,
                                      data.uuid,
                                      data.anon,
                                      socket.id);
            all_sessions.push(session);
            debugNodeSessions();
            // find all the sockets of the target
            // and emit to all of 'em
            var this_sessions_sockets = [socket];
            _.filter(all_sockets, function(i) {
                // get all sockets of target
                if (i.username == data.target) {
                    if (i.sessions) {
                        i.sessions.push(session);
                    } else {
                        i.sessions = [session];
                    }

                    this_sessions_sockets.push(i);
                }
            });

            // open session in all of them
            this_sessions_sockets.forEach(function(ii) {
                ii.emit('new_session', session);
            });
        } else {
            throw('eww!!');
        }
    });

    socket.on('message', function(message) {
        console.log('message');
        console.dir(message);
        if (!(message.content && message.direction && message.session)) {
            throw('bad message, bad kitty!!');
        }

        var session = _.find(all_sessions, function(i){
            return i.uuid == message.session.uuid;
        });

        var target_sockets = _.filter(all_sockets, function(i) {
            return i.username == message.session.target.username;
        });

        if (!(session && target_sockets.length > 0)) {
            console.dir(session);
            throw('eww!');
        }

        var anon_socket = _.find(all_sockets, function(i) {
            return i.id == session.anon.socket_id;
        });

        if (!anon_socket) {
            throw('not anon socket');
        }

        // add socket of anon to target sockets
        target_sockets.push(anon_socket);
        // emit to all parties
        target_sockets.forEach(function(socket){
            socket.emit('new_message', message);
        });

        target_sockets.length = 0;
    });

    socket.on('disconnect', function () {
        var i = all_sockets.indexOf(socket);
        console.log("Socket disconnected: " + socket.id);
        console.log('User disconnected: ' + socket.username);
        all_sockets.splice(i, 1); // remove element

        // search for socket username
        if (socket.username) {
            // redis op
            removeSocketFromUser(socket.username, socket.id);
            // any client left for this user?

            var has_sockets = false;
            _.filter(all_sockets, function(i) {
                if (i.username == socket.username) {
                    has_sockets = true;
                }
            });

            //
            if (_.find(all_sockets, function(i){return i.username == socket.username}) == undefined) {
                console.log('no sockets remaining for user ' + socket.username + " delete all sessions");
                // inform all users and anon that this user really disconnected
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
        debugNodeSockets();
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

        debugNodeSockets();
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
        if (ii.sessions) {
            ii.sessions.forEach(function(session) {
                console.log(">>>   " + session);
            });
        }
    });
    console.log("---before----");
};


function debugNodeSessions() {
    console.log("---before----");
    all_sessions.forEach(function(ii) {
        console.dir(">>> session.target: " + ii.target);
        console.log(">>> session.uuid: " + ii.uuid);
        console.dir(">>> session.anon: " + ii.anon);
    });
    console.log("---before----");
};
