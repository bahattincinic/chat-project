'use strict';

angular.module('mainApp').controller('searchController', function($scope, accountService){
    $scope.searchText = '';
    $scope.search = {'is_search': false, 'user': [], 'network':[]};
    // search input keyup query
    $scope.$watch('searchText', function (val) {
        var payload = {'q': val};
        if(val =! ''){
            accountService.search(payload, function(data){
                if(data.data.users.length > 0 || data.data.networks.length > 0){
                    $scope.search.is_search = true;
                    $scope.search.user = data.data.users;
                    $scope.search.network = data.data.networks;
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