// authentication resource
angular.module('authApp').factory('authService', function($http) {
    return {
        login: function(payload, successCallback, errorCallback){
            payload = angular.toJson(payload);
            $http.post('/api/v1/auth/login/session/', payload).then(successCallback, errorCallback)
        },
        register: function(payload, successCallback, errorCallback){
            payload = angular.toJson(payload);
            $http.post('/api/v1/account/', payload).then(successCallback, errorCallback)
        },
        logout: function(successCallback){
            $http.get('/api/v1/auth/logout/session/').success(successCallback);
        },
        forgot_password: function(payload, successCallback, errorCallback){
            payload = angular.toJson(payload);
            $http.put('/api/v1/auth/forgot/password/', payload).then(successCallback, errorCallback)
        },
        forgot_username: function(payload, successCallback, errorCallback){
            payload = angular.toJson(payload);
            $http.put('/api/v1/auth/forgot/username/', payload).then(successCallback, errorCallback)
        },
        new_password: function(payload, successCallback, errorCallback){
            payload = angular.toJson(payload);
            $http.put('/api/v1/auth/forgot/new-password/', payload).then(successCallback, errorCallback)
        }
    }
});