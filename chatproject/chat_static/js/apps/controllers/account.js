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
            $rootScope.follow = { visibility: $rootScope.authenticate, text: '', state: false };
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
    '$scope', 'accountService', '$rootScope', function($scope, accountService, $rootScope){
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
            $scope.form.state = true;
            $scope.form.visibility = true;
            $scope.form.error_header = 'Settings Saved';
            $scope.form.error_message = 'Your settings has been successfully updated.';
        }, function(data){
            $scope.form.state = false;
            $scope.form.visibility = true;
            $scope.form.error_header = 'Settings not saved';
            $scope.form.error_message = '';
            angular.forEach(data.data, function(value, key){
                $scope.form.error_message += ' ' +  value;
            });
        });
    };
}]);



accountApp.controller('changePasswordController', [
    '$scope', 'accountService', '$rootScope', function($scope, accountService, $rootScope){

    // change password forn
    $scope.form = {state:false, visibility:false, error_heade:'', error_message:''};

    // account change password
    $scope.change_password = function(){
        accountService.change_password($rootScope.user.username, $rootScope.user, function(){
            $scope.form.state = true;
            $scope.form.visibility = true;
            $scope.form.error_header = 'Settings Saved';
            $scope.form.error_message = 'Password Changed';
        }, function(data){
            $scope.form.state = false;
            $scope.form.visibility = true;
            $scope.form.error_header = 'Settings not saved';
            $scope.form.error_message = '';
            angular.forEach(data.data, function(value, key){
                $scope.form.error_message += value[0];
            });
        });
    };
}]);


