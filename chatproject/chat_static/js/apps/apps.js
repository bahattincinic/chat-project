'use strict';

// Define all modules with no dependencies
// authantication application
angular.module('authApp', []);
// chat application
angular.module('chatApp', []);
// network application
angular.module('networkApp', []);

// Angular Apps
var ANGULAR_APPS = ['ngAnimate', 'ngRoute', 'ngResource'];
// Local Apps
var LOCAL_APPS = ['authApp', 'chatApp', 'networkApp'];
// All Apps
var INSTALLED_APPS = ANGULAR_APPS.concat(LOCAL_APPS);

// Define  "main" module and inject all other modules as dependencies
angular.module('mainApp', INSTALLED_APPS).config(['$httpProvider', function($httpProvider) {
  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);