var _ = require('underscore');
var xredis = require('./xredis');

var all_sockets = [];

exports.all_sockets = all_sockets;

exports.addSocket = function(socket) {
    all_sockets.push(socket);
    if (socket.handshake.sessionid) {
        xredis.bindUserSocket(socket, socket.handshake.sessionid);
    }
}

exports.removeSocket = function(socket) {
    var i = all_sockets.indexOf(socket);
    all_sockets.splice(i, 1);
}

exports.getSocket = function(socket__id) {
    if (!socket__id) {
        throw('no id submitted');
    }

    var socket = _.find(all_sockets, function(i) {
        return i.id == socket__id;
    });

    if (!socket) {
        throw('failed to find socket: id ' + socket__id);
    }

    return socket;
}

exports.noSocketsLeft = function(username) {
    return _.find(all_sockets, function(i){return i.username == username}) == undefined
}

function get_user_sockets(username) {
    return _.filter(all_sockets, function(socket){ return socket.username == username});
}

exports.getUserSockets = get_user_sockets;

exports.addSessionToTargetSockets = function(username, session) {
    var sockets = get_user_sockets(username);
    sockets.forEach(function(i){
        if (i.sessions) {
            i.sessions.push(session);
        } else {
            i.sessions = [session];
        }
    });

    return sockets;
}

exports.removeSessionFromTargetSockets = function (username, session) {
    // session >> session__uuid
    var sockets = get_user_sockets(username);
    sockets.forEach(function(ii) {
        if (ii.sessions && ii.sessions.length > 0 && _.contains(ii.sessions, session)) {
            var k = ii.sessions.indexOf(session);
            ii.sessions.splice(k, 1);
        }
    });
    // return relevant sockets
    return sockets;
}

exports.addSessionToSocket = function(session__uuid, socket) {
    if (socket && session__uuid) {
        if (socket.sessions) {
            socket.sessions.push(session__uuid);
        } else {
            socket.sessions = [session__uuid];
        }
    }
};

