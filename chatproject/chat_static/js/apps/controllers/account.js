'use strict';

var accountApp = angular.module('accountApp');

accountApp.controller('followController', [
    '$scope', 'accountService', '$rootScope', function($scope, accountService, $rootScope){

    // get user follows
    $scope.ajaxCall.promise.then(function() {
        if($rootScope.state == 'me'){
            $rootScope.user.follows_page = { 'page':1 };
            accountService.follows($rootScope.user.username, $rootScope.user.follows_page, function(data){
                $rootScope.user.follows = data.data.results;
                $rootScope.user.load_more_follow = data.data.count >= 10;
            });
        }else if($rootScope.authenticate){
            $scope.follow = { visibility: $rootScope.authenticate, text: '', state: false };
                accountService.check_follow($rootScope.user.username, function(data){
                   if(data.data.count > 0){
                        $scope.follow.text = 'Un Follow';
                        $scope.follow.state = true;
                   }else{
                        $scope.follow.text = 'Follow';
                        $scope.follow.state = false;
                   }
            });
        }
    });

    // user follows pagination
    $scope.loadFollows = function(){
        $rootScope.user.follows_page.page = $rootScope.user.follows_page + 1;
        accountService.follows($rootScope.user.username, $rootScope.user.follows_page.page, function(data){
            angular.forEach(data.data.results, function(value, key){
                $rootScope.user.follows.push(value);
            });
            $rootScope.user.load_more_follow = data.data.count >= 10;
        });
    };

    // Follow
    $scope.do_follow = function(){
       if($scope.follow.state && $rootScope.authenticate){
        // unfollow - DELETE
        accountService.unfollow($scope.user.username, function(){
            $scope.follow.state = false;
            $scope.follow.text = 'Follow';
        });
       }else if($rootScope.authenticate){
        // follow - POST
        accountService.follow($scope.user.username, function(){
            $scope.follow.state = true;
            $scope.follow.text = 'Un Follow';
        });
       }
    }
}]);



accountApp.controller('updateProfile', [
    '$scope', 'accountService', '$rootScope', 'alertService', function($scope, accountService, $rootScope, alertService){

    // form elements
    $scope.form = {
      gender: [
          {id:'male', name:'Male'},
          {id:'female', name:'Female'},
          {id:'other', name:'Other'}
      ], sound: [
          {id:true, name:'On'},
          {id:false, name:'Off'}
      ]
    };
    // update action
    $scope.update_profile = function(){
        var form = angular.copy($rootScope.user);
        delete form.avatar;
        delete form.background;
        accountService.update_profile($scope.user.username, form, function(data){
            $scope.alert = alertService.success('Settings saved', 'Your settings has been successfully updated.');
        }, function(data){
            var message = '';
            angular.forEach(data.data, function(value, key){
                message += ' ' +  value;
            });
            $scope.alert = alertService.error('Settings not saved', message);
        });
    };
}]);



accountApp.controller('changePasswordController', [
    '$scope', 'accountService', '$rootScope', 'alertService', function($scope, accountService, $rootScope, alertService){

    // account change password
    $scope.change_password = function(){
        accountService.change_password($rootScope.user.username, $rootScope.user, function(){
            $scope.alert = alertService.success('Settings saved', 'Password Changed');
        }, function(data){
            var message = '';
            angular.forEach(data.data, function(value, key){
                message += ' ' +  value[0];
            });
            $scope.alert = alertService.error('Settings not saved', message);
        });
    };
}]);


accountApp.controller('reportController', function($scope, accountService, $rootScope, $location){
    $scope.form = {text: ''};

    $scope.report = function(){
        accountService.report($rootScope.user.username, $scope.form, function(){
            $location.path('/');
        });
    };
});


accountApp.controller('changeAvatarController', function($scope, accountService, $rootScope){
    $scope.form = {avatar: '', cover:''};
    $scope.ajaxCall.promise.then(function() {
        $scope.form.avatar = $rootScope.user.avatar_url;
        $scope.form.cover = $rootScope.user.background_url;
    });
});