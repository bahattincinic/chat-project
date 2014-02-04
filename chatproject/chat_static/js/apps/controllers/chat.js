'use strict';

angular.module('chatApp').controller('userChatController' ,[
    '$scope', '$filter', 'socket','chatService', function($scope, $filter, socket, chatService) {
    // All Session list
    $scope.session_list = [];
    $scope.content = {'content': ''};

    // Socket
    socket.on('session_' + $scope.user.username, function(session) {
        var tmpSesssion = JSON.parse(session);
        tmpSesssion.messages = [];
        $scope.session_list.push(tmpSesssion);
        if(!$scope.active_session){
            $scope.active_session = tmpSesssion;
        }
        socket.on('session_' + tmpSesssion.uuid, function(data){
            var sessionFilter = $filter('filter')($scope.session_list, tmpSesssion.uuid)[0]
            sessionFilter.messages.push(JSON.parse(data));
        });
    });

    // Chat Session Close
    $scope.blockSession = function(){

    };
    // Chat Session Change status active
    $scope.sessionChangeStatus = function($event, item){
       $scope.active_session = item;
    };
    // Session new message
    $scope.createMessage = function(){
        chatService.message($scope.content,
                            $scope.user.username,
                            $scope.active_session.uuid,
                            function(data){
            $scope.content.content = '';
        });
    };
}]);


angular.module('chatApp').controller('anonChatController',[
    '$scope', 'socket', 'chatService', 'accountService', function($scope, socket, chatService, accountService) {
    // messages
    $scope.messages = [];
    // input
    $scope.content = {'content': ''};
    // New Session
    $scope.createSession = function(){
        if(!$scope.session &&  $scope.content.content != ''){
            chatService.session($scope.user.username, function(data){
                $scope.session = data.data;
                $scope.createMessage();
                socket.on('session_' + $scope.session.uuid, function(data){
                    $scope.messages.push(JSON.parse(data));
                });
            });
        }
    };
    // New Message
    $scope.createMessage = function(){
        if($scope.session && $scope.content.content != ''){
            chatService.message($scope.content,
                                $scope.user.username,
                                $scope.session.uuid,
                                function(data){
                $scope.content.content = '';
            })
        }else{
            $scope.createSession();
        }
    };
    // check follow state
    $scope.checkFollowState = function(state){
        $scope.user.follow = { visibility: state, text: '', state: false };
        if(state){
            accountService.check_follow($scope.user.username, function(data){
               if(data.count > 0){
                    $scope.user.follow.text = 'Un Follow';
                    $scope.user.follow.state = true;
               }else{
                    $scope.user.follow.text = 'Follow';
                    $scope.user.follow.state = false;
               }
            });
        }
    };
    // Follow
    $scope.do_follow = function(){
       if($scope.user.follow.state){
        // unfollow - DELETE
        accountService.unfollow($scope.user.username, function(){
            $scope.user.follow.state = false;
            $scope.user.follow.text = 'Follow';
        });
       }else{
        // follow - POST
        accountService.follow($scope.user.username, function(){
            $scope.user.follow.state = true;
            $scope.user.follow.text = 'Un Follow';
        });
       }
    }
}]);