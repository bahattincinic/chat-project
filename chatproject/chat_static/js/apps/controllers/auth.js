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
            var errors = []
            angular.forEach(data.data, function(value, key){
              this.push(key + ': ' + value[0]);
            }, errors);
            $scope.errorMessage = errors
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