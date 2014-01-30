// multi
// zadd ll 1401301233 balkan
// zadd ll 1401301235 osman
// zadd ll 1401301240 kazim
// zadd ll 1401301223 haci
// zadd ll 1401301220 burak
// exec

// -----
var redis = require('redis').createClient();

var args = ["ll",
            1401301233, "balkan",
            1401301235, "osman",
            1401301240, "kazim",
            1401301223, "haci",
            1401301220, "burak"]
var side = ['ll', 1401301333, "bulk"]

// clean
redis.del('ll');

// exec a multi
var multi = redis.multi();
multi.zadd(args);
multi.zadd(side);
multi.keys("*");
multi.exec(function(err, response) {
    if (err) throw err;
    console.log('added:multi: ' + response + " items");
    console.log('type: ' + typeof(response));
    response.forEach(function(reply, index) {
        console.log("reply: " + reply + " of index: " + index + " with typeof " + typeof(reply));
        if (typeof(reply) == 'object') {
            console.log("object");
            // reply.forEach(function (ins, index) {
            //     console.log( "(" +index+ ")" +  "inner obj: " + ins);
            // })
        }
    });
});

// redis.multi()
//     .keys("*")
//     .zadd(args, function(err, response) {
//         if (err) throw err;
//         console.log('added' + response + " items.(exp 5)");
//         redis.keys("*", function(err, response) {
//             if (err) throw err;
//             console.log("inner keys returned: " + response);
//         });
//     })
//     .zadd(side, function(err, response) {
//         if (err) throw err;
//         console.log('added' + response + " items.(exp 1)");
//     })
//     .keys("*")
//     .exec(function(err, replies) {
//         if (err) throw err;
//         console.log('multi got ' + replies.length + 'no of replies');
//         replies.forEach(function(reply, index) {
//             console.log('reply no: ' + index + ': ' + reply.toString());
//         });
//     });
