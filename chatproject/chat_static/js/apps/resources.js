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
        }
    }
});