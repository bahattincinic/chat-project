var redis = require('redis').createClient(),
    moment = require('moment');

var redisSocketPrefix = 'sockets_'; // sockets_<username>
var redisSessionPrefix = 'sessions_'; // sessions_<username>
var redisSingleSessionPrefix = 'session_'; // session_<sesion__uuid>

exports.redis = redis;

exports.bindUserSocket = function(socket, sessionid) {
    if (socket && sessionid) {
        console.log(sessionid);
        redis.get('djsession:' + sessionid, function(err, reply) {
            try {
                var buffer = new Buffer(reply, 'base64').toString();
                var add = buffer.split(':')[0] + ":";
                var djsession = JSON.parse(buffer.replace(add, ''));
                var userid = djsession["_auth_user_id"];
                socket.username = userid;
                // update rank for this user
                updateRank(socket.username);
            } catch(err) {
                console.error("error parsing user session:  " + err);
                throw(err);
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
        if (err) throw err;
        console.log(response);
    });
    console.log('xxx');
}

exports.updateUserRank = updateRank;

