angular.module('mainApp').run(['$rootScope', '$location', 'accountService', function($rootScope, $location, accountService) {

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