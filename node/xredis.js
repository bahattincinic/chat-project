var redis = require('redis').createClient(),
    moment = require('moment');

var redisSocketPrefix = 'sockets_'; // sockets_<username>
var redisSessionPrefix = 'sessions_'; // sessions_<username>
var redisSingleSessionPrefix = 'session_'; // session_<sesion__uuid>

exports.bindUserSocket = function(socket, sessionid) {
    if (socket && sessionid) {
        var key = 'djsession:' + sessionid;
        redis.get(key, function(err, reply) {
            if (err) {
                throw new Error('Unable to get session data from redis: ' + key +
                    ' skipping binding user to socket message:' + err);
            }

            if (reply) {
                try {
                    // try to parse session data
                    var buffer = new Buffer(reply, 'base64').toString();
                    var add = buffer.split(':')[0] + ":";
                    var djsession = JSON.parse(buffer.replace(add, ''));
                    var userid = djsession["_auth_user_id"];
                    socket.username = userid;
                    // update rank for this user
                    updateRank(socket.username);
                } catch(err) {
                    var message =  'Unable to parse session data for sessionid: ' +
                        sessionid + " message:" + err;
                    console.error(message);
                }
            } else {
                console.warn('no session data returned for sessionid: ' + sessionid);
            }
        });
    }
}

exports.removeSocket = function(username, socket__id) {
    console.log('removeSocketFromUser: ' + username + " id: " + socket__id);
    // remove this socket from redis
    redis.srem(redisSocketPrefix + username, socket__id);
    // if there are no sockets left for this user, then
    // delete all sessions and sockets
    redis.scard(redisSocketPrefix + username, function(err, count) {
        if (err) throw err;
        console.log(count + " number of sockets for " + username);

        if (count == 0) {
            console.log('deleting all for ' + username);
            var multi = redis.multi();
            multi.del(redisSocketPrefix + username);
            multi.del(redisSessionPrefix + username);
            multi.exec(function(err, response) {
                if (err) throw err;
            });
        }
    });
}

exports.addSocket = function(username, socket__id) {
    if (username && socket__id) {
        redis.sadd(redisSocketPrefix + username, socket__id);
    } else {
        throw('addSocket err');
    }
}

exports.removeSession = function(session__uuid) {
    redis.del(redisSessionPrefix + session__uuid);
}

exports.removeSessionFromUser = function(username, session) {
    if (username && session) {
        var key = redisSessionPrefix + username;
        redis.srem(key, session);
        // TODO: if scard == 0 then delete
        redis.scard(key, function(err, count) {
            if (count == 0) {redis.del(key);}
        });
    }
}

exports.addSessionToUser = function(username, session) {
    if (username && session) {
        redis.sadd(redisSessionPrefix + username, session);
    }
}

function updateRank(username) {
    // score is current date
    var score = parseInt(moment().format('YYMMDDHHmm'));
    var args = ["active_connections", score, username];
    var multi = redis.multi();
    multi.zadd(args);
    multi.exec(function(err, response) {
        if (err) throw new Error("Error while executing update multi " +
            "on redis: " + err);
    });
    console.log('xxx');
}

exports.updateUserRank = updateRank;

