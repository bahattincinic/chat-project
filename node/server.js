var app = require('http').createServer(),
    io = require('socket.io').listen(app),
    moment = require('moment'),
    _ = require('underscore');
    logger = io.log,
    redis = require('redis'),
    xss = require('./xsessions'),
    ;
// used when storing socket values in redis
var redisSocketPrefix = 'sockets_';
var redisSessionPrefix = 'sessions_';

app.listen(9999);

var all_sockets = [];

io.configure(function() {
    io.set('close timeout', 60*60*24); // 24h
    io.set('log level', 1);
});

// subscriber = redis.createClient();
// var spattern = "new_session";
// // subscriber.psubscribe(spattern);
// var mpattern = "message_*";
// subscriber.psubscribe(mpattern);
updater = redis.createClient();


io.sockets.on('connection', function(socket) {
    console.log('on connection');
    all_sockets.push(socket);

    socket.on('initiate_session', function(data) {
        console.log('initiate_session');
        if (data.anon && data.uuid && data.target) {
            var session = new xss.Session(data.target,
                                          data.uuid,
                                          data.anon,
                                          socket.id);
            xss.addSession(session);
            // find all the sockets of the target
            // and emit to all of 'em
            var this_sessions_sockets = [socket];
            all_sockets.forEach(function(i){
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

        var session = xss.getSession(message.session.uuid);

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

            // any other sockets left for this user
            if (_.find(all_sockets, function(i){return i.username == socket.username}) == undefined) {
                console.log('no sockets remaining: ' + socket.username + " delete all sessions");
                // inform all users and anon that this user really disconnected
                if (socket.sessions && socket.sessions.length > 0) {
                    socket.sessions.forEach(function(session) {
                        closeSession(session);
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
        // triggered when user herself closes session voluntarily
        console.log("disconnected: " + data.user + " session.id: " + data.uuid);
        console.log('socket.id: ' + socket.id + " socket.user: " + socket.username);
        var session = xss.getSession(data.uuid);
        if (session) {closeSession(session);} else {throw('not found session')}
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


function getAnonSocket(socket__id) {
    var socket = _.find(all_sockets, function(i){
        return i.id == socket__id;
    });
    if (!socket) {
        throw('failed to find anon socket');
    }
    return socket;
}

function getSession(session__uuid) {
    var session = _.find(all_sessions, function(i){
        return i.uuid == session__uuid;
    });

    if (!session) {
        throw('unable to find session');
    }
    return session;
};

function getTargetSockets (username) {
    var target_sockets = _.filter(all_sockets, function(i) {
        return i.username == username;
    });

    return target_sockets;
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
};


function closeSession (session) {
    if (session.uuid) {
        // find targets to inform
        var pending_notification = getTargetSockets(session.target.username);

        // remove this session from target sessions
        pending_notification.forEach(function(ii) {
            if (ii.sessions && ii.sessions.length > 0 && _.contains(ii.sessions, session)) {
                removeSessionFromSocketSessions(ii, session.uuid);
            }
        });

        // find anon socket to inform and add it to list
        pending_notification.push(getAnonSocket(session.anon.socket_id));

        // inform all targets
        if (pending_notification.length > 0) {
            pending_notification.forEach(function (socket) {
                socket.emit('close_session', {
                    target: session.target,
                    uuid: session.uuid,
                    anon: session.anon});
            });
        }

        // reset pending notification
        pending_notification.length = 0;

        // remove session from all resources (redis and node)
        xss.removeSession(session);
    } else {
        throw('no uuid for session');
    }
};