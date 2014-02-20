'use strict';

angular.module('mainApp').config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/', {
        templateUrl: '/static/js/apps/views/account_chat.html',
        action: 'chatApp.chatController',
        access: '*'
    }).when('/follows', {
        templateUrl: '/static/js/apps/views/account_follows.html',
        action: 'accountApp.followController',
        access: 'me'
    }).when('/edit-profile', {
        templateUrl: '/static/js/apps/views/account_edit.html',
        action: 'accountApp.updateProfile',
        access: 'me'
    }).when('/change-password', {
        templateUrl: '/static/js/apps/views/account_change_password.html',
        action: 'accountApp.changePasswordController',
        access: 'me'
    }).when('/report', {
        templateUrl: '/static/js/apps/views/anon_report.html',
        action: 'accountApp.reportController',
        access: 'anon'
    }).otherwise({
       redirectTo: '/'
    });
}]).run(function ($rootScope, $timeout, $filter, socket, $q, $location) {
    $rootScope.$on("$routeChangeStart", function (event, next, current) {
        // permisson Control
        if(next.access != '*' && next.access != $rootScope.state){
            $location.path('/');
        }
        if(next.originalPath == '/' && $rootScope.state == 'anon'){
            next.templateUrl = '/static/js/apps/views/anon_chat.html';
        }
    });
    // get selected user
    $rootScope.ajaxCall = $q.defer();
    $rootScope.getActiveUser(function(data){
        $rootScope.user = data;
        $rootScope.is_loading = false;
        $rootScope.session_list = [];
        if($rootScope.state == 'me'){
            socket.on('session_' + $rootScope.user.username, function(session) {
                var tmpSesssion = JSON.parse(session);
                tmpSesssion.messages = [];
                $rootScope.session_list.push(tmpSesssion);
                if(!$rootScope.active_session){
                    $rootScope.active_session = tmpSesssion;
                }
                socket.on('session_' + tmpSesssion.uuid, function(data){
                    var sessionFilter = $filter('filter')($rootScope.session_list, tmpSesssion.uuid)[0];
                    sessionFilter.messages.push(JSON.parse(data));
                });
                $rootScope.user.follows = [];
            });
        }
        $timeout(function(){$rootScope.is_loading = false;}, 500);
        $rootScope.ajaxCall.resolve();
    });
});
