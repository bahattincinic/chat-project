'use strict';

angular.module('mainApp').controller('searchController', function($scope, accountService, $rootScope){
    $scope.searchText = '';
    $scope.search = {'is_search': false, 'user': [], 'network':[]};

    $scope.toggleMenu = function(){
      console.log('searchController::toggleMenu()');
      $rootScope.showmenu = $rootScope.showmenu ? false : true;
    };

    // search input keyup query
    $scope.$watch('searchText', function (val) {
        var payload = {'q': val};
        if(val =! '' && val.length > 2){
            accountService.search(payload, function(data){
                if(data.users.length > 0 || data.networks.length > 0){
                    $scope.search.is_search = true;
                    $scope.search.user = data.users;
                    $scope.search.network = data.networks;
                }else{
                    $scope.close();
                }
            });
        }else{
           $scope.close();
        }
    });

    $scope.close = function(){
        $scope.search.is_search = false;
        $scope.search.user = [];
        $scope.search.network = [];
    }
});