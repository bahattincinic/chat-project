// authentication resource
angular.module('authApp').factory('authService', function($http, $resource, ConfigService, UrlService) {
    var endpoint = ConfigService.get('api_endpoint');
    return {
        login: function(payload, successCallback, errorCallback){
            payload = angular.toJson(payload);
            var url = UrlService.parse(':endPoint/auth/login/session/', {'endPoint': endpoint});
            $http.post(url, payload).then(successCallback, errorCallback)
        },
        register: function(payload, successCallback, errorCallback){
            payload = angular.toJson(payload);
            var url = UrlService.parse(':endPoint/account/', {'endPoint': endpoint});
            $http.post(url, payload).then(successCallback, errorCallback)
        },
        logout: function(successCallback){
            var url = UrlService.parse(':endPoint/auth/logout/session/', {'endPoint': endpoint});
            $http.get(url).success(successCallback);
        },
        forgot_password: function(payload, successCallback, errorCallback){
            payload = angular.toJson(payload);
            var url = UrlService.parse(':endPoint/auth/forgot/password/', {'endPoint': endpoint});
            $http.put(url, payload).then(successCallback, errorCallback)
        },
        forgot_username: function(payload, successCallback, errorCallback){
            payload = angular.toJson(payload);
            var url = UrlService.parse(':endPoint/auth/forgot/username/', {'endPoint': endpoint});
            $http.put(url, payload).then(successCallback, errorCallback)
        },
        new_password: function(payload, successCallback, errorCallback){
            payload = angular.toJson(payload);
            var url = UrlService.parse(':endPoint/auth/forgot/new-password/', {'endPoint': endpoint});
            $http.put(url, payload).then(successCallback, errorCallback)
        }
    }
});

// Node Resource
angular.module('mainApp').factory('socket', function ($rootScope, ConfigService) {
  var url = ConfigService.get('node_url');
  var socket = io.connect(url, {resource: 'io'});
  return {
    on: function (eventName, callback) {
      socket.on(eventName, function () {
        var args = arguments;
        $rootScope.$apply(function () {
          callback.apply(socket, args);
        });
      });
    },
    emit: function (eventName, data, callback) {
      socket.emit(eventName, data, function () {
        var args = arguments;
        $rootScope.$apply(function () {
          if (callback) {
            callback.apply(socket, args);
          }
        });
      })
    },
    pulse: function(){
        socket.emit('pulse');
    }
  };
});

// Chat Resource
angular.module('chatApp').factory('chatService', function($http, ConfigService, UrlService){
    var endpoint = ConfigService.get('api_endpoint');
    return {
        session: function(username, successCallback, errorCallback){
            var url = UrlService.parse(':endPoint/v1/account/:username/sessions/',{
                'endPoint': endpoint, 'username': username});
            $http.post(url).then(successCallback, errorCallback)
        },
        message: function(payload, username, uuid , successCallback, errorCallback){
            payload = angular.toJson(payload);
            var url = UrlService.parse(':endPoint/v1/account/:username/sessions/:uuid/messages/',{
                'endPoint': endpoint, 'username': username, 'uuid': uuid});
            $http.post(url, payload).then(successCallback, errorCallback)
        }
    }
});

// User Service
angular.module('chatApp').factory('accountService', function($http, $cacheFactory, ConfigService, UrlService){
    var endpoint = ConfigService.get('api_endpoint');
    return {
        check_follow: function(username, successCallback, errorCallback){
            var url = UrlService.parse(':endPoint/account/:username/follow/', {
                'endPoint': endpoint, 'username': username});
            $http.get(url).then(successCallback, errorCallback);
        },
        follow: function(username, successCallback, errorCallback){
            var url = UrlService.parse(':endPoint/account/:username/follow/', {
                'endPoint': endpoint, 'username': username});
            $http.post(url).then(successCallback, errorCallback);
        },
        unfollow: function(username, successCallback, errorCallback){
            var url = UrlService.parse(':endPoint/account/:username/follow/', {
                'endPoint': endpoint, 'username': username});
            $http.delete(url).then(successCallback, errorCallback);
        },
        user_profile: function(username, successCallback, errorCallback){
            var url = UrlService.parse(':endPoint/account/:username/', {
                'endPoint': endpoint, 'username': username});
            $http.get(url).then(successCallback, errorCallback);
        },
        follows: function(username, payload, successCallback, errorCallback){
            var url = UrlService.parse(':endPoint/account/:username/follows/', {
                'endPoint': endpoint, 'username': username});
            $http.get(url, {params: payload}).then(successCallback, errorCallback);
        },
        update_profile: function(username, payload, successCallback, errorCallback){
            var url = UrlService.parse(':endPoint/account/:username/', {
                'endPoint': endpoint, 'username': username});
            payload = angular.toJson(payload);
            $http.put(url, payload).then(successCallback, errorCallback);
        },
        change_password: function(username, payload, successCallback, errorCallback){
            var url = UrlService.parse(':endPoint/account/:username/change-password/', {
                'endPoint': endpoint, 'username': username});
            payload = angular.toJson(payload);
            $http.put(url, payload).then(successCallback, errorCallback);
        },
        report: function(username, payload, successCallback, errorCallback){
            var url = UrlService.parse(':endPoint/account/:username/report/', {
                'endPoint': endpoint, 'username': username});
            $http.post(url, payload).then(successCallback, errorCallback);
        },
        search: function(payload, successCallback, errorCallback){
            var key = 'searchkey_' + payload.q;
            var url = UrlService.parse(':endPoint/search/', {'endPoint': endpoint});
            if($cacheFactory.get(key) == undefined || $cacheFactory.get(key) == ''){
                $http.get(url, {params: payload}).then(
                    function(data){
                        $cacheFactory(key).put('result', data.data);
                        successCallback(data.data);
                    },function(data){
                        var tmp = {'users': [], 'networks': []};
                        $cacheFactory(key).put('result', tmp);
                        errorCallback(tmp);
                    }
                );
            }else{
                successCallback($cacheFactory.get(key).get('result'));
            }
        }
    }
});


// Shuffle Resource
angular.module('mainApp').factory('shuffleService', function($http, ConfigService, UrlService){
    var endpoint = ConfigService.get('api_endpoint');
    return {
        all: function(successCallback){
            var url = UrlService.parse(':endPoint/shuffle/all/', {'endPoint': endpoint});
            $http.get(url).then(successCallback);
        },
        network: function(name, successCallback){
            var url = UrlService.parse(':endPoint/shuffle/network/:name/', {
                'endPoint': endpoint, 'name': name});
            $http.get(url).then(successCallback);
        }
    }
});