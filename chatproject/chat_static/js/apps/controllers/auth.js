'use strict';

/* Login Controller */
angular.module('authApp').controller('loginController' ,[
    '$scope', 'authService', function($scope, authService) {
    // Form Fields
    $scope.form = {'username': '', 'password': ''};
    // Login Process
    $scope.process = function(){
        authService.login($scope.form, function(data){
            location.reload();
        }, function(data){
            $scope.alert = {
                visibility: true,
                title: 'Error',
                message: 'Invalid username or password.'
            };
        });
    };
}]);

/* Register Controller */
angular.module('authApp').controller('registerController',[
    '$scope', 'authService', '$rootScope', function($scope, authService, $rootScope) {
    // Form Fields
    $scope.form = {'username': '', 'password': '', 'email': ''};
    // Login Process
    $scope.process = function(){
        authService.register($scope.form, function(data){
            $scope.alert = {
                visibility: true,
                title: 'Success',
                message: 'Registration process is successful'
            };
            $scope.form.email = '';
            $scope.form.username = '';
            $scope.form.password = '';
        }, function(data){
            $scope.alert = {
                visibility: true,
                title: 'Error',
                message: $rootScope.ErrorRenderer(data.data)
            };
        });
    };
}]);

// Logout Controller
angular.module('authApp').controller('logoutController', [
    '$scope', 'authService', function($scope, authService) {
    // logout process
    $scope.process = function(){
        authService.logout(function(){
            location.reload();
        });
    };
}]);

// Forgot Password Controller
angular.module('authApp').controller('forgotPasswordController', [
    '$scope', 'authService', '$rootScope', function($scope, authService, $rootScope) {
    $scope.title = 'Forgot my Password';
    $scope.p_type = 'password';
    $scope.form = {'email': ''};

    // change Forgot type
    $scope.changeProcess = function(p_type){
        if(p_type=='password'){
            $scope.title = 'Forgot my Password';
            $scope.p_type = 'password';
        }else if(p_type=='username'){
            $scope.title = 'Forgot my Username';
            $scope.p_type = 'username';
        }
    };
    //pending request
    $scope.process = function(){
        var api_method;
        if($scope.p_type == 'password'){
            api_method = authService.forgot_password;
        }else{
            api_method = authService.forgot_username;
        }
        api_method($scope.form, function(data){
            $scope.alert = {
                visibility: true,
                title: 'Success',
                state: true,
                message: $scope.form.email + ' mail send'
            };
            $scope.form.email = '';
        }, function(data){
            $scope.alert = {
                visibility: true,
                title: 'Error',
                state: false,
                message: $rootScope.ErrorRenderer(data.data)
            };
        });
    };
}]);

// New Password
angular.module('authApp').controller('newPasswordController', [
    '$scope', 'authService', '$rootScope', function($scope, authService, $rootScope) {
    $scope.form = {'email': '', 'secret_key': '', 'new_password': '', 'confirm_password': ''};
    $scope.process = function(){
        if($scope.form.new_password != '' &&
            $scope.form.confirm_password != '' &&
            $scope.form.new_password == $scope.form.confirm_password){
            authService.new_password($scope.form, function(data){
                $scope.alert = {
                    visibility: true,
                    title: 'Success',
                    state: true,
                    message: 'Changed Password'
                };
                setInterval(function(){ window.location = '/'; }, 1000);
            }, function(data){
                $scope.alert = {
                    visibility: true,
                    title: 'Error',
                    state: false,
                    message: $rootScope.ErrorRenderer(data.data)
                };
            });
        }else{
            $scope.alert = {
                visibility: true,
                title: 'Error',
                state: false,
                message: 'passwords did not match'
             };
        }
    };
}]);