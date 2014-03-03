var serafin = angular.module('serafin', ['ngAnimate']);

serafin.controller('pages', ['$scope', function(scope) {
    scope.index = 0;
    scope.limit = 0;

    scope.next = function() {
        if (scope.index < scope.limit - 1)
            scope.index++;
    };
    scope.prev = function() {
        if (scope.index > 0)
            scope.index--;
    };
}]);

serafin.directive('page', function() {
    return {
        restrict: 'C',
        link: function(scope, element, attrs) {
            scope.limit++;
        }
    };
});

