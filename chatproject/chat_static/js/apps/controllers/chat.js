'use strict';

angular.module('chatApp').controller('userChatController' ,[
    '$scope', 'chatService', function($scope, chatService) {
    // Active Chat Session
    $scope.active_session = {};
    // All Session list
    $scope.session_list = [];
    // Chat Session Close
    $scope.blockSession = function(){

    };
    // Chat Session Change status active
    $scope.sessionChangeStatus = function($event, item){
       $scope.active_session = item;
    };
    // Session new message
    $scope.createMessage = function(){

    };
}]);


angular.module('chatApp').controller('anonChatController',[
    '$scope', 'chatService', function($scope, chatService) {
    // messages
    $scope.messages = [];
    // from user
    $scope.from = {};
    // to user
    $scope.to = {};
    // session
    $scope.session = {};
    // Session new message
    $scope.createMessage = function(){

    };
}]);