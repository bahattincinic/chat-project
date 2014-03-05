'use strict';

angular.module('chatApp').controller('chatController', [
    '$scope', '$rootScope', 'chatService', 'socket', '$filter', function($scope, $rootScope, chatService, socket, $filter){

    // All Session list
    $scope.content = {'content': ''};

    // on new sessions for this client
    socket.on('new_session', function(session) {
        session.messages = [];
        session.is_closed = false;
        session.is_typing = false;
        $rootScope.session_list.push(session);
        if(!$rootScope.active_session){
            $rootScope.active_session = session;
        }
    });

    // on new messages for this client
    socket.on('new_message', function(message) {
        var session = $filter('filter')($rootScope.session_list, message.session.uuid)[0];
        session.messages.push(message);
        if(session.uuid == $rootScope.active_session.uuid){
            $rootScope.active_session = session;
        }
    });

    // on close sessions
    socket.on('close_session', function(session) {
        var check = $filter('filter')($rootScope.session_list, session.uuid);
        if(check.length > 0){
            check = check[0];
            check.is_closed = true;
            check.is_typing = false;
            if(check.uuid == $rootScope.active_session.uuid){
                $rootScope.active_session = check;
            }
        }
    });

    // user is typing event
    $scope.typing = function(){
      var content = $scope.content.content;
      var data = {
          'direction': $rootScope.state == 'me'? 'TO_ANON': 'TO_USR',
          'uuid': $scope.active_session.uuid,
          'action': 'start'
      };
      if(content != '' && typeof content != 'undefined' && $scope.active_session){
          data.action = 'start';
          socket.emit('typing', data);
      }else if($scope.active_session){
          data.action = 'stop';
          socket.emit('typing', data);
      }
    };

    // user typing
    socket.on('typing_started', function(data) {
        var check = $filter('filter')($rootScope.session_list, data.uuid);
        if(check.length > 0){
            check = check[0];
            check.is_typing = true;
            if(check.uuid == $rootScope.active_session.uuid){
                $rootScope.active_session = check;
            }
        }
    });

    // user is not typing
    socket.on('typing_stopped', function(data) {
        var check = $filter('filter')($rootScope.session_list, data.uuid);
        if(check.length > 0){
            check = check[0];
            check.is_typing = false;
            if(check.uuid == $rootScope.active_session.uuid){
                $rootScope.active_session = check;
            }
        }
    });

    // Chat Session Close
    $scope.closeSession = function(){
        if($rootScope.active_session){
          socket.emit('user_disconnected', $rootScope.active_session);
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
                    // is not typing
                    $scope.typing();
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