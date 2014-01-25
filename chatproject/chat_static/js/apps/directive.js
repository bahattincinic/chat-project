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