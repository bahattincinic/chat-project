var d = require('domain').create();

d.on('error', function(err) {
    // log message and exit
    console.error('fatal: ' + err.message);
    // cleanup
    process.exit(1);
});

d.run(function() {
    var app = require('http').createServer(),
        io = require('socket.io').listen(app),
        xsocket = require('./xsockets'),
        xsession = require('./xsessions'),
        cookie_reader = require('cookie'),
        xredis = require('./xredis');
    // used when storing socket values in redis
    app.listen(9999);

    io.configure(function() {
        io.set('authorization', function(handshakeData, accept) {
            if (handshakeData.headers.cookie) {
                handshakeData.cookie = cookie_reader.parse(handshakeData.headers.cookie);
                if (handshakeData.cookie['sessionid']) {
                    handshakeData.sessionid = handshakeData.cookie['sessionid'];
                }

                return accept(null, true);
            }
            // no cookie no connection
            return accept('no cookie', false);
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

    io.sockets.on('connection', function(socket) {
        console.log('connection socket with id: ' + socket.id);
        xsocket.addSocket(socket);
        socket.on('error', function(err) {
            console.log('socket io error here: ' + err);
            throw new Error(err);
        });

        socket.on('initiate_session', function(data) {
            console.log('initiate_session');
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
                xredis.addSessionToUser(session);
                // TODO: store session or socket data on redis also
            } else {
                throw new Error('unexpected/missing args when initiating session: ' + data);
            }
            console.log('initiate done');
        });

        socket.on('message', function(message) {
            console.dir(message);
            if (!(message.content && message.direction && message.session)) {
                throw new Error('unexpected/missing args ' +
                    'when relaying message: ' + message);
            }

            var session = xsession.getSession(message.session.uuid);
            if (!session) {
                throw new Error('unable to find session to send message');
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
                // redis op
//            xredis.removeSocket(socket.username, socket.id);

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

        socket.on('pulse', function() {
            if (socket.username) {
                xredis.updateUserRank(socket.username);
            }
        });
    });

    function closeSession(session) {
        console.log('close session');
        if (session.uuid && session.target.username) {
            var pending_notification = xsocket.removeSessionFromTargetSockets(session.target.username, session.uuid);
            xredis.removeSessionFromUser(session.target.username, session.uuid);
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
            xredis.removeSessionFromUser(session);
        } else {
            throw('invalid session to close');
        }
    };
});


