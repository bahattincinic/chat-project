'use strict';

// Define all your modules with no dependencies
angular.module('authApp', []);
angular.module('chatApp', []);
angular.module('networkApp', []);

// Lastly, define your "main" module and inject all other modules as dependencies
angular.module('mainApp', [
    // Angular Apps
    'ngAnimate',
    'ngRoute',
    'ngResource',
    // Local Apps
    'authApp',
    'chatApp',
    'networkApp'
]).config(['$httpProvider', function($httpProvider) {
  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);