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
    scope.variables = {};

    http.get(api + window.location.search).success(function(data) {
        scope.getVariables(data.data);
        scope.title = data.title;
        scope.page = data.data;
        scope.dead_end = data.dead_end;
    });

    scope.$on('title', function(event, data) {
        scope.title = data;
    });

    scope.getVariables = function(data) {
        data.forEach(function(pagelet) {
            for (var variableName in pagelet.variables) {
                scope.variables[variableName] = pagelet.variables[variableName];
            }
        });
    }
}]);

serafin.controller('pages', ['$scope', '$http', function(scope, http) {
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
            scope.getVariables(data.data);
            scope.$emit('title', data.title);
            scope.page = data.data;
            scope.dead_end = data.dead_end;
            scope.form.submitted = false;
            window.scrollTo(0,0);
        });
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

serafin.directive('checkboxlist', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs, ngModel) {

            var clScope = scope.$parent.$parent;

            if (clScope.field && clScope.field.required) {
                clScope.subForm.$setValidity(
                    'required',
                    clScope.field.value.length > 0
                )
            }

            scope.toggle = function(list, item) {
                var index = list.indexOf(item);
                if (index == -1) {
                    list.push(item);
                } else {
                    list.splice(index, 1);
                }

                if (clScope.field && clScope.field.required) {
                    clScope.subForm.$setValidity(
                        'required',
                        list.length > 0
                    )
                }
            };

            scope.$watch('alt.selected', function(newVal, oldVal) {
                if (newVal) {
                    scope.pagelet.content.text = scope.alt.text;
                } else {
                    scope.pagelet.content.text = '';
                }
            });
        }
    }
});

serafin.directive('title', function() {
    return {
        restrict: 'CE',
        link: function(scope, element, attrs) {
            scope.$watch('title', function(newVal, oldVal) {
                if (newVal !== oldVal) {
                    element.text(scope.title);
                }
            });
        }
    };
});

serafin.directive('liveinput', ['$rootScope', function(rootScope) {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function(scope, element, attrs, ngModel) {
            scope.$watch(function () {
                return ngModel.$modelValue;
            }, function(newVal) {
                if (!newVal) newVal = '...'
                rootScope.variables[scope.$parent.field.variable_name] = newVal;
            });
        }
    };
}]);

serafin.filter('breaks', ['$sce', function (sce) {
    return function (value) {
        var broken = value.replace(/(?:\r\n|\r|\n)/g, '<br>');
        return sce.trustAsHtml(broken);
    };
}]);

serafin.directive('livereplace', ['$compile', function(compile) {
    return {
        restrict: 'A',
        controller: 'pages',
        scope: {
            text: '=livereplace',
        },
        link: function(scope, element, attrs) {
            scope.variables = scope.$parent.variables;
            scope.$watch('text', function() {
                var template = scope.text;
                var compiled = compile(template)(scope);
                element.html('');
                element.append(compiled);
            })
        }
    };
}]);

serafin.directive('menu', ['$timeout', function(timeout) {
    return {
        restrict: 'C',
        link: function(scope, element, attrs) {
            var win = angular.element(window)
            win.on('resize', function() {
                timeout(function() {
                    scope.desktop = win[0].innerWidth > 640;
                    scope.menu = win[0].innerWidth > 640;
                });
            })
            win.triggerHandler('resize');

            scope.toggleMenu = function() {
                if (!scope.desktop) {
                    scope.menu = !scope.menu;
                }
            }
        }
    }
}])
