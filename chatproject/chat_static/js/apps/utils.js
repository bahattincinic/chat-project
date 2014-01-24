angular.module('mainApp').run(['$rootScope', function($rootScope) {

 // Api Error format
 $rootScope.ErrorRenderer = function(data) {
   var errors = [];
   angular.forEach(data, function(value, key){
      this.push(key + ': ' + value[0]);
   }, errors);
   return errors;
 };

}]);