var app = require('http').createServer(),
    io = require('socket.io').listen(app),
    xsocket = require('./xsockets'),
    xsession = require('./xsessions'),
    cookie_reader = require('cookie'),
    _ = require('underscore'),
    xredis = require('./xredis');
// used when storing socket values in redis
app.listen(9998);

io.configure(function() {
    io.set('authorization', function(handshakeData, accept) {
        if (handshakeData.headers.cookie) {
            handshakeData.cookie = cookie_reader.parse(handshakeData.headers.cookie);
            if (handshakeData.cookie['sessionid']) {
                handshakeData.sessionid = handshakeData.cookie['sessionid'];
            }
        }
        // allow connection always
        return accept(null, true);
    });
    io.set('close timeout', 60*60*24); // 24h
    io.set('log level', 1);
    io.set('resource', '/io');
    io.set('transports', [
        'websocket'
        , 'flashsocket'
        , 'htmlfile'
        , 'xhr-polling'
        , 'jsonp-polling'
    ]);
});

io.sockets.on('connection', function(socket){
    console.log('connection socket with id: ' + socket.id);
    xsocket.addSocket(socket);

    socket.on('error', function(err) {
        console.log('socket io error here: ' + err);
        throw new Error(err);
    });

    socket.on('initiate_session', function(data) {
        console.log('initiate_session..');
        console.dir(data);
        if (data.anon && data.uuid && data.target) {
            var session = xsession.createSession(
                data.target,
                data.uuid,
                data.anon,
                socket.id);
            //
            var sockets = xsocket.addSessionToTargetSockets(data.target, session.uuid);
            sockets.forEach(function(ii){ii.emit('new_session', session)});
            socket.emit('new_session', session);
            // TODO: store session or socket data on redis also
        } else {
            throw new Error('unexpected/missing args when initiating session: ' + data);
        }
    });

    socket.on('message', function(message) {
        console.log('message..');
        console.dir(message);
        if (!(message.content && message.direction && message.session)) {
            console.error('unexpected/missing args ' +
                'when relaying message: ' + message);
            return;
        }

        var session = xsession.getSession(message.session.uuid);
        if (!session) {
            console.error('unable to find session to send message');
            return;
        }

        var target_username = message.session.target.username;
        var target_sockets = xsocket.getUserSockets(target_username);
        if (!target_sockets.length > 0) {
            throw new Error('No target sockets found ' +
                'while sending message for username: ' + target_username);
        }

        var anon_socket = xsocket.getSocket(session.anon.socket_id);
        // add socket of anon to target sockets
        target_sockets.push(anon_socket);
        // emit to all parties
        target_sockets.forEach(function(socket){
            socket.emit('new_message', message);
        });

        target_sockets.length = 0;
        console.log('message delivered');
    });

    socket.on('disconnect', function () {
        console.log("Socket disconnected: " + socket.id);
        console.log('User disconnected: ' + socket.username);
        xsocket.removeSocket(socket);

        // check if this socket has any anon sessions
        if (xsession.hasAnonSessions(socket.id)) {
            var sessions = xsession.getAnonSessions(socket.id);
            sessions.forEach(function(session) {
                session.anon_closed = true;
                closeSession(session);
            });
            sessions.length = 0;
        }

        // search for target sessions
        if (socket.username) {
            // any other sockets left for this user
            if (xsocket.noSocketsLeft(socket.username)) {
                console.log('no sockets remaining: ' + socket.username + " delete all sessions");
                // inform all users and anon that this user really disconnected
                if (socket.sessions && socket.sessions.length > 0) {
                    socket.sessions.forEach(function(session__uuid) {
                        closeSession(xsession.getSession(session__uuid));
                    });
                    // remove all sessions from removed socket
                    socket.sessions.length = 0;
                }

                // remove from rank as well
                xredis.removeUserFromRank(socket.username);
            } else {
                console.log('remaining sockets does exists for user ' + socket.username);
            }
        }
    });

    socket.on('user_disconnected', function(data) {
        // triggered when user closes session voluntarily
        console.log('socket.id: ' + socket.id + " socket.user: " + socket.username);
        var session = xsession.getSession(data.uuid);
        if (session) {closeSession(session);} else {throw('not found session')}
    });

    socket.on('typing', function(data) {
        console.log('typing...');
        console.dir(data);
        var session = sanitizeTyping(data);
        if (session) {
            if (data.direction == 'TO_ANON') {
                // get all sockets for target
                var socket_id = session.anon.socket_id;
                if (!socket_id) {
                    console.error('unable to determine anon socket id');
                    return;
                }

                var anon_socket = xsocket.getSocket(socket_id);
                if (anon_socket) {
                    var channel = '';
                    if (data.action == 'start') {
                        channel = 'typing_started';
                    } else {
                        channel = 'typing_stopped';
                    }

                    anon_socket.emit(channel, data);
                }
            } else {
                var username = session.target.username;
                var target_sockets = xsocket.getUserSockets(username);
                if (target_sockets && target_sockets.length > 0) {
                    target_sockets.forEach(function(socket) {
                        var channel = '';
                        if (data.action == 'start') {
                            channel = 'typing_started';
                        } else {
                            channel = 'typing_stopped';
                        }
                        socket.emit(channel, data);
                    })
                }
            }
        }
    });

    socket.on('pulse', function() {
        if (socket.username) {
            xredis.updateUserRank(socket.username);
        }
    });
});

function closeSession(session) {
    console.log('close session');
    if (session && session.uuid && session.target.username) {
        var pending_notification = xsocket.removeSessionFromTargetSockets(session.target.username, session.uuid);
        // find anon socket to inform and add it to list
        if (!session.anon_closed) {
            pending_notification.push(xsocket.getSocket(session.anon.socket_id));
        }

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
        xsession.removeSession(session);
    } else {
        console.error('invalid session to close');
        console.log('all sessions:');
        xsession.all_sessions.forEach(function(session) {
            console.dir(session);
        });
    }
}

function sanitizeTyping(data) {
    if (!(data && data.uuid && data.direction)) {
        console.error('invalid typing data');
        return null;
    }

    if (!_.contains(['TO_USR','TO_ANON'], data.direction)) {
        console.error('invalid direction data');
        return null;
    }

    var session = xsession.getSession(data.uuid);
    if (!session) {
        console.error('invalid session data to relay typing.');
        return null;
    }
    if (!_.contains(['start', 'stop'], data.action)) {
        console.error('action must be either start or stop during typing event');
        return null;
    }

    return session;
}