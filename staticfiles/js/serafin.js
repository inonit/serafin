var serafin = angular.module('serafin', ['ngAnimate']);

serafin.config(['$httpProvider', function(httpProvider) {
    httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    httpProvider.defaults.headers.post['X-CSRFToken'] = csrf_token;
    if (!httpProvider.defaults.headers.get) {
        httpProvider.defaults.headers.get = {};
    }
    // disable IE AJAX request caching
    httpProvider.defaults.headers.get['If-Modified-Since'] = '0';
}]);

serafin.run(['$rootScope', '$http', function(scope, http) {
    scope.title = '...';
    scope.page = {};

    http.get(api + window.location.search).success(function(data) {
        scope.title = data['title'];
        scope.page = data['data'];
        scope.dead_end = data['dead_end'];
    });

    scope.$on('title', function(event, data) {
        scope.title = data;
    });
}]);

serafin.controller('pages', ['$scope', '$http', '$sce', function(scope, http, sce) {

    scope.next = function() {
        scope.form.submitted = true;
        if (scope.form.$invalid) {
            return;
        }

        var data = [];
        scope.page.forEach(function(pagelet) {
            if (['form', 'quiz'].indexOf(pagelet.content_type) > -1) {
                pagelet.content.forEach(function(field) {
                    data.push({
                        key: field.variable_name,
                        value: field.value,
                    });
                });
            }
            if (['toggleset', 'togglesetmulti'].indexOf(pagelet.content_type) > -1) {
                data.push({
                    key: pagelet.content.variable_name,
                    value: pagelet.content.value,
                });
            }
        });

        var request = {
            method: 'POST',
            url: api + '?next=1',
            data: data,
        };

        http(request).success(function(data) {
            scope.$emit('title', data['title']);
            scope.page = data['data'];
            scope.dead_end = data['dead_end'];
            scope.form.submitted = false;
        });
    };

    scope.trust = function(html) {
        return sce.trustAsHtml(html);
    };

}]);

serafin.directive('page', function() {
    return {
        restrict: 'C',
        link: function(scope, element, attrs) {
            scope.form.submitted = false;
        }
    };
});

serafin.controller('checkboxlist', ['$scope', function(scope) {
    scope.toggle = function(list, item) {
        var index = list.indexOf(item);
        if (index == -1) {
            list.push(item);
        } else {
            list.splice(index, 1);
        }
    };
    scope.$watch('alt.selected', function(newVal, oldVal) {
        if (newVal) {
            scope.pagelet.content.text = scope.alt.text;
        } else {
            scope.pagelet.content.text = '';
        }
    });
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
