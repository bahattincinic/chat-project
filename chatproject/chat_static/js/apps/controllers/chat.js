'use strict';

angular.module('chatApp').controller('chatController', [
    '$scope', '$rootScope', 'chatService', 'socket', function($scope, $rootScope, chatService, socket){

    // All Session list
    $scope.content = {'content': ''};

    // Chat Session Close
    $scope.blockSession = function(){

    };

    // Chat Session Change status active
    $scope.sessionChangeStatus = function($event, item){
       $rootScope.active_session = item;
    };

    // Session new message
    $scope.createMessage = function(){
        if($rootScope.active_session && $scope.content.content != ''){
            chatService.message(
                $scope.content,
                $rootScope.user.username,
                $rootScope.active_session.uuid,
                function(data){
                    $scope.content.content = '';
            });
        }

        if($rootScope.state == 'anon' && !$rootScope.session){
            $scope.createSession();
        }
    };

    // anon user create session
    $scope.createSession = function(){
        if(!$rootScope.active_session &&  $scope.content.content != '' && $rootScope.state == 'anon'){
            chatService.session($rootScope.user.username, function(data){
                var tmpSesssion = data.data;
                tmpSesssion.messages = [];
                $rootScope.active_session = tmpSesssion;
                $scope.createMessage();
                socket.on('session_' + $scope.active_session.uuid, function(data){
                    $scope.active_session.messages.push(JSON.parse(data));
                });
            });
        }
    };

}]);