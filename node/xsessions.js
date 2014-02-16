var _ = require('underscore');

var all_sessions = [];


exports.all_sessions = all_sessions;

function Session(target, uuid, anon, anon_socket_id) {
    this.target = {'username': target};
    this.uuid = uuid;
    this.anon = {'username': anon,
                 'socket_id': anon_socket_id};
}


exports.createSession = function(target, uuid, anon, anon_socket_id) {
    var session = new Session(target, uuid, anon, anon_socket_id);
    all_sessions.push(session);
    return session;
}


exports.getSession = function(session__uuid) {
    return _.find(all_sessions, function(i) {
        return i.uuid == session__uuid;
    });
}

exports.removeSession = function(session) {
    // TODO: check ops here!
    if (session.uuid) {
        var k = all_sessions.indexOf(session.uuid);
        all_sessions.splice(k, 1);
        // delete from redis
        // updater.del(redisSessionPrefix + data.uuid);
    }
}

exports.hasAnonSessions = function(socket__id) {
    if (_.find(all_sessions, function(ii) { return ii.anon.socket_id == socket__id }) == undefined) {
        return false;
    }
    return true;
}

exports.getAnonSessions = function(socket__id) {
    var sessions =  _.filter(all_sessions, function(ii){return ii.anon.socket_id == socket__id;});
    if (sessions.length == 0) {
        throw('no session found for anon');
    }
    return sessions;
}