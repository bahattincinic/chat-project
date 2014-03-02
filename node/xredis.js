var redis = require('redis').createClient(),
    http = require('http'),
    _ = require('underscore'),
    xsocket = require('./xsockets'),
    moment = require('moment');

var redisSocketPrefix = 'sockets_'; // sockets_<username>
var redisSessionPrefix = 'sessions_'; // sessions_<username>
var redisSingleSessionPrefix = 'session_'; // session_<sesion__uuid>

function restoreMore(socket) {
    if (socket.username) {
        var username = socket.username;
        // get sessions from redis
        var key = redisSessionPrefix + username;
        redis.scard(key, function(err, count) {
            if (err) throw new Error('err while getting ' +
                'user sessions from redis: ' + err);

            if (!(count > 0)) {
                return;
            }

            redis.smembers(key, function(err, resp) {
                if (!(resp.length > 0)) {
                    return;
                }

                console.log('sessions found continue to restore');
                resp.forEach(function(session__uuid) {
                    xsocket.addSessionToSocket(session__uuid, socket);
                });
            })
        });
    }
}

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
                    if (userid) {
                        var options = {
                            host: '127.0.0.1',
                            port: 80,
                            path: '/internal/translate/' + userid + '/'
                        };
                        // make request
                        http.get(options, function(resp){
                            resp.on('data', function(rawdata) {
                                var response = JSON.parse(new Buffer(rawdata, 'ascii').toString());
                                if (_.has(response, 'username')) {
                                    socket.username = response.username;
                                    updateRank(socket.username);
                                    restoreMore(socket);
                                } else {
                                    // log this error
                                    console.error('username not found for id: ' + userid);
                                }
                            });
                        }).on('error', function(e) {
                                throw new Error('Error while using internal api, ' +
                                    'userid: ' + userid + "error: " + e.message);
                        });
                    }
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

exports.removeSessionFromUser = function(session) {
    if (session && session.target && session.target.username && session.uuid) {
        var key = redisSessionPrefix + session.target.username;
        redis.srem(key, session.uuid);
        // TODO: if scard == 0 then delete
        redis.scard(key, function(err, count) {
            if (count == 0) {redis.del(key);}
        });
    }
}

exports.addSessionToUser = function(session) {
    if (session && session.target && session.target.username && session.uuid) {
        redis.sadd(redisSessionPrefix + session.target.username, session.uuid);
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
}

exports.updateUserRank = updateRank;

