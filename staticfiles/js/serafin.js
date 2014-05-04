var serafin = angular.module('serafin', ['ngAnimate']);

serafin.config(['$httpProvider', function(httpProvider) {
    httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    httpProvider.defaults.headers.post['X-CSRFToken'] = csrf_token;
}]);

serafin.run(['$rootScope', '$http', function(scope, http) {
    scope.title = '...';
    scope.page = {};

    http.get(api + window.location.search).success(function(data) {
        scope.title = data['title'];
        scope.page = data['data'];
    });

    scope.$on('title', function(event, data) {
        scope.title = data;
    });
}]);

serafin.controller('pages', ['$scope', '$http', '$sce', function(scope, http, sce) {

    scope.next = function() {
        var data = [];
        scope.page.forEach(function(pagelet) {
            if (pagelet.content_type == 'form') {
                pagelet.content.forEach(function(field) {
                    data.push({
                        variable_name: field.variable_name,
                        value: field.value,
                    });
                });
            }
        });

        var request = {
            method: 'GET',
            url: api,
        };

        if (data.length > 0) {
            request.method = 'POST';
            request.data = data;
        }

        http(request).success(function(data) {
            scope.$emit('title', data['title']);
            scope.page = data['data'];
            scope.index++;
        });
    };

    scope.trust = function(html) {
        return sce.trustAsHtml(html);
    };

}]);

serafin.directive('title', function() {
    return {
        restrict: 'CE',
        link: function(scope, element, attrs) {
            scope.$watch('title', function(oldVal, newVal) {
                if (newVal !== oldVal) {
                    element.text(scope.title);
                }
            });
        }
    };
});
