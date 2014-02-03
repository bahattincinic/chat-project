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
    '$scope', 'socket', 'chatService', function($scope, socket, chatService) {
    // messages
    $scope.messages = [];
    // input
    $scope.content = {'content': ''};
    // Session new message
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
}]);