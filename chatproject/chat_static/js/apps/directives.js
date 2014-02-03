angular.module('mainApp').directive('backgroundImage', function(){
    return function(scope, element, attrs){
        // string to scope instange
        var url = scope.$eval(attrs.backgroundImage);
        element.css({
            'background-image': 'url(' + url + ')',
            'background-size' : 'cover'
        });
    };
});


angular.module('chatApp').directive('comment', function(){
    return {
        restrict: 'E',
        scope: {
            instance: '=instance'
        },
        templateUrl: '/static/js/apps/views/comment.html'
    };
});