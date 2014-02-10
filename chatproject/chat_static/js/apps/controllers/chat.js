'use strict';

angular.module('chatApp').controller('userChatController' ,[
    '$scope', '$filter', 'socket','chatService', '$rootScope', 'accountService', '$timeout',
        function($scope, $filter, socket, chatService, $rootScope, accountService, $timeout) {
    // All Session list
    $scope.session_list = [];
    $scope.content = {'content': ''};

    $rootScope.getActiveUser(function(data){
        $scope.user = data;
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
            $scope.user.follows = [];
        });
        $timeout(function(){$scope.is_loading = false;}, 500);
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

    // get user follows
    $scope.getFollows = function(){
        $scope.user.follows_page = { 'page':1 };
        accountService.follows($scope.user.username, $scope.user.follows_page, function(data){
            $scope.user.follows = data.data.results;
            $scope.user.load_more_follow = data.data.count >= 10;
            $scope.page = 'follows';
        });
    };

    $scope.loadFollows = function(){
        $scope.user.follows_page.page = $scope.user.follows_page + 1;
        accountService.follows($scope.user.username, $scope.user.follows_page, function(data){
            angular.forEach(data.data.results, function(value, key){
                $scope.user.follows.push(value);
            });
            $scope.user.load_more_follow = data.data.count >= 10;
        });
    };

    $scope.goBack = function(){
        $scope.page = 'chat';
    }

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
               if(data.data.count > 0){
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