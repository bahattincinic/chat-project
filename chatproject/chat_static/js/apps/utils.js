var mainApp = angular.module('mainApp');

mainApp.run(['$rootScope', '$location', 'accountService', function($rootScope, $location, accountService) {

 // Api Error format
 $rootScope.ErrorRenderer = function(data) {
   var errors = [];
   angular.forEach(data, function(value, key){
      this.push(key + ': ' + value[0]);
   }, errors);
   return errors;
 };

 // Get Active User
 $rootScope.getActiveUser = function(callback){
    var username = $location.absUrl().split('/');
    if(username.length > 3 && username[3] != ''){
       accountService.user_profile(username[3], function(data){
          callback(data.data);
       });
    }
 };

}]);


mainApp.service('alertService', function(){
    // error alert
    this.error = function(title, message){
       return {
            visibility: true,
            title: title,
            state: false,
            message: message
       }
   };
   // success alert
   this.success = function(title, message){
       return {
            visibility: true,
            title: title,
            state: true,
            message: message
       }
   };
});


mainApp.service('ConfigService', function (){
    var _environments = {
        local: {
            host: 'l',
            config: {
                api_endpoint: '/api/v1',
                node_url: 'http://l:9998'
            }
        },
        prod: {
            host: 'chat.burakalkan.com',
            config: {
                api_endpoint: '/api/v1',
                node_url: 'http://chat.burakalkan.com:9998'
            }
        }
    }, _environment;

    this.getEnvironment = function () {
        var host = window.location.host;
        if (_environment) {
            return _environment;
        }
        for (var environment in _environments) {
            if (typeof _environments[environment].host && _environments[environment].host == host) {
                _environment = environment;
                return _environment;
            }
        }
        return null;
    };
    this.get = function (property) {
        return _environments[this.getEnvironment()].config[property];
    };
});


mainApp.service('UrlService', function () {
    this.parse = function (url, data) {
        angular.forEach(data, function (value, key) {
            url = url.replace(":" + key, value);
        });
        return url;
    }
});