var _ = require('underscore');

var all_sessions = [];

function Session(target, uuid, anon, anon_socket_id) {
    this.target = {'username': target};
    this.uuid = uuid;
    this.anon = {'username': anon,
                 'socket_id': anon_socket_id};
};

// exports
// session type
exports.Session = Session;

exports.addSession = function(session) {
    all_sessions.push(session);
};

exports.getSession = function(session__uuid) {
    return _.find(all_sessions, function(i) {
        return i.uuid == session__uuid;
    });
};

exports.removeSession = function(session) {
    // TODO: check ops here!
    if (session.uuid) {
        var k = all_sessions.indexOf(session.uuid);
        all_sessions.splice(k, 1);
        // delete from redis
        // updater.del(redisSessionPrefix + data.uuid);
    }
};