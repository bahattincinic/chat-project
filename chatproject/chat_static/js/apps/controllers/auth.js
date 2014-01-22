'use strict';

/* Login Controller */
angular.module('authApp').controller('loginController' ,['$scope', 'authService', function($scope, authService) {
    // Form Fields
    $scope.form = {'username': '', 'password': ''};
    // Login Process
    $scope.process = function(){
        authService.login($scope.form, function(data){
            location.reload();
        }, function(data){
            $scope.isError = true;
        });
    };
}]);

/* Register Controller */
angular.module('authApp').controller('registerController', ['$scope', 'authService', function($scope, authService) {
    // Form Fields
    $scope.form = {'username': '', 'password': '', 'email': ''};
    // Login Process
    $scope.process = function(){
        authService.register($scope.form, function(data){
            $scope.errorType = "Success";
            $scope.form.email = '';
            $scope.form.username = '';
            $scope.form.password = '';
            $scope.isError = true;
            $scope.errorMessage = 'Registration process is successful';
        }, function(data){
            $scope.errorType = "Error";
            $scope.isError = true;
            var errors = [];
            angular.forEach(data.data, function(value, key){
              this.push(key + ': ' + value[0]);
            }, errors);
            $scope.errorMessage = errors;
        });
    };
}]);

// Logout Controller
angular.module('authApp').controller('logoutController', ['$scope', 'authService', function($scope, authService) {
    // logout process
    $scope.process = function(){
        authService.logout(function(){
            location.reload();
        });
    };
}]);

// Forgot Password Controller
angular.module('authApp').controller('forgotPasswordController', ['$scope', 'authService', function($scope, authService) {
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
            $scope.isMessage = true;
            $scope.isSuccess = true;
            $scope.errorTitle = 'Success';
            $scope.erorrMessage = $scope.form.email + ' mail send';
        }, function(data){
            $scope.isMessage = true;
            $scope.isError = true;
            $scope.errorTitle = 'Error';
            var errors = [];
            angular.forEach(data.data, function(value, key){
              this.push(key + ': ' + value[0]);
            }, errors);
            $scope.erorrMessage = errors;
        });
    };
}]);