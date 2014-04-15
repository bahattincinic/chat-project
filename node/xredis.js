var redis = require('redis').createClient(),
    http = require('http'),
    _ = require('underscore'),
    moment = require('moment');

exports.bindUserSocket = function(socket, sessionid) {
    if (socket && sessionid) {
        var key = 'djsession:' + sessionid;
        redis.get(key, function(err, reply) {
            if (err) {
                throw new Error('Unable to get session data from redis: ' + key +
                    ' skipping binding user to socket message: ' + err);
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
                            host: 'chat.burakalkan.com',
                            port: 80,
                            path: '/internal/translate/' + userid + '/'
                        };
                        // make request
                        http.get(options, function(resp){
                            resp.on('data', function(rawdata) {
                                var response = JSON.parse(new Buffer(rawdata, 'ascii').toString());
                                if (_.has(response, 'username')) {
                                    console.log(">>> setting socket username as " + response.username);
                                    socket.username = response.username;
                                    updateRank(socket.username);
//                                    restoreMore(socket);
                                } else {
                                    // log this error
                                    console.error('username not found for id: ' + userid);
                                }
                            });
                        }).on('error', function(e) {
                                throw new Error('Error while using internal api (django), ' +
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
};

function updateRank(username) {
    if (username) {
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
}

function removeUserFromRank(username) {
    if (username) {
        redis.zrem('active_connections', username);
    }
}

exports.updateUserRank = updateRank;
exports.removeUserFromRank = removeUserFromRank;

