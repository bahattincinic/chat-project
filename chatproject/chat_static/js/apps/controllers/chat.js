'use strict';

angular.module('chatApp').controller('chatController', [
    '$scope', '$rootScope', 'chatService', 'socket', '$filter', function($scope, $rootScope, chatService, socket, $filter){

    // All Session list
    $scope.content = {'content': ''};

    // on new sessions for this client
    socket.on('new_session', function(session) {
        session.messages = [];
        $rootScope.session_list.push(session);
        if(!$rootScope.active_session){
            $rootScope.active_session = session;
        }
    });

    // on new messages for this client
    socket.on('new_message', function(message) {
        var session = $filter('filter')($rootScope.session_list, message.session.uuid)[0];
        session.messages.push(message);
    });

    // on close sessions
    socket.on('close_session', function(session) {
        // code
    });

    // Chat Session Close
    $scope.closeSession = function(){
        if($rootScope.active_session){
          socket.emit('user_disconnected', $rootScope.active_session);
          $rootScope.active_session.is_closed = true;
        }
    };

    // Chat Session Change status active
    $scope.sessionChangeStatus = function($event, item){
       $rootScope.active_session = item;
    };

    // Session new message
    $scope.createMessage = function(){
        if($rootScope.active_session && $scope.content.content != ''){
            chatService.message($scope.content, $rootScope.user.username, $rootScope.active_session.uuid,
                function(data){
                    socket.emit('message', data.data);
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
                var session = data.data;
                session.messages = [];
                var socket_data = {
                    'anon': session.anon.username,
                    'uuid': session.uuid,
                    'target': session.target.username
                };
                $rootScope.active_session = session;
                socket.emit('initiate_session', socket_data);
                $scope.createMessage();
            });
        }
    };

}]);