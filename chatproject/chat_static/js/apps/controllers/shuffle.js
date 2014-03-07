'use strict';

/* Shuffle Controller */
angular.module('mainApp').controller('shuffleController', function($scope, shuffleService){
    // shuffle list
    $scope.shuffle_list = [];

    // reflesh shuffle
    $scope.reflesh = function(){
        shuffleService.all(function(data){
            $scope.shuffle_list = data.data['results'];
        });
    };

    $scope.reflesh();
});


// Shuffle Network Controller
angular.module('mainApp').controller('shuffleNetworkController', function($scope, shuffleService){

});