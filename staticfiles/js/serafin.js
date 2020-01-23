var serafin = angular.module('serafin', ['serafinTopbarMenu']);

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

    if (api) {
        http.get(api + window.location.search).then(response => {
            scope.error = null;
            scope.getVariables(response.data.data);
            scope.title = response.data.title;
            scope.page = response.data.data;
            scope.dead_end = response.data.dead_end;
            scope.stacked = response.data.stacked;
            scope.is_chapter = response.data.is_chapter;
            scope.chapters = response.data.chapters;
        }, reason => {
            scope.error = reason.data;
            scope.page = {};
        });
    }

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
    var timerStart = new Date();

    var read_form_data = function() {
        var data = {};
        scope.page.forEach(function(pagelet) {
            if (pagelet.content_type == 'form' ||
                pagelet.content_type == 'quiz') {
                pagelet.content.forEach(function(field) {
                    data[field.variable_name] = field.value
                });
            }
            if (pagelet.content_type == 'toggleset' ||
                pagelet.content_type == 'togglesetmulti') {
                data[pagelet.content.variable_name] = pagelet.content.value
            }
            if (pagelet.content_type == 'expression') {
                data['expression_' + pagelet.content.variable_name] = pagelet.content.value
            }
        });
        return data;
    };

    scope.next = function() {
        scope.form.submitted = true;
        if (scope.form.$invalid) {
            return;
        }

        var data = read_form_data();
        var timerEnd = new Date();
        var timeSpent = timerEnd.getTime() - timerStart.getTime();
        data.timer = timeSpent;

        var url = (scope.dead_end && scope.stacked ? api + '?pop=1' : api + '?next=1');
        var request = {
            method: 'POST',
            url: url,
            data: data,
        };

        http(request).then(response => {
            scope.error = null;
            scope.getVariables(response.data.data);
            scope.$emit('title', response.data.title);
            scope.page = response.data.data;
            scope.dead_end = response.data.dead_end;
            scope.stacked = response.data.stacked;
            scope.is_chapter = response.data.is_chapter;
            scope.chapters = response.data.chapters;
            scope.form.submitted = false;
            window.scrollTo(0,0);
        }, reason => {
            scope.error = reason.data;
            scope.page = {};
        });
    };

    scope.chapter_url = function (chapter_id) {
        var data = read_form_data();
        if (Object.entries(data).length > 0) {
             var answer = confirm("Are you sure you want to leave?");
             if (!answer) {
                 return;
             }
        }
        var timerEnd = new Date();
        var timeSpent = timerEnd.getTime() - timerStart.getTime();
        data.timer = timeSpent;

        var url = (api + '?chapter=' + chapter_id);
        var request = {
            method: 'POST',
            url: url,
            data: data,
        };

        http(request).then(response => {
            scope.error = null;
            scope.getVariables(response.data.data);
            scope.$emit('title', response.data.title);
            scope.page = response.data.data;
            scope.dead_end = response.data.dead_end;
            scope.stacked = response.data.stacked;
            scope.is_chapter = response.data.is_chapter;
            scope.chapters = response.data.chapters;
            scope.form.submitted = false;
            window.scrollTo(0,0);
        }, reason => {
            scope.error = reason.data;
            scope.page = {};
        });
    }
}]);

serafin.directive('page', function() {
    return {
        restrict: 'C',
        link: function(scope, element, attrs) {
            if (scope.form) {
                scope.form.submitted = false;
            };
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

serafin.directive('stringToNumber', function() {
  return {
    require: 'ngModel',
    link: function(scope, element, attrs, ngModel) {
      ngModel.$parsers.push(function(value) {
        return '' + value;
      });
      ngModel.$formatters.push(function(value) {
        return parseFloat(value, 10);
      });
    }
  };
});

serafin.filter('breaks', ['$sce', function (sce) {
    return function (value) {
        var broken = value.toString().replace(/(?:\r\n|\r|\n)/g, '<br>');
        return sce.trustAsHtml(broken);
    };
}]);

serafin.filter('stripzerodecimal', function () {
    return function (value) {
        if (typeof value != 'number')
          return value;
        return value.toString().replace(/\.0$/, '');
    };
});

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
                if (template) {
                    var compiled = compile(template)(scope);
                    element.html('');
                    element.append(compiled);
                }
            })
        }
    };
}]);

serafin.directive('richtextlivereplace', ['$compile', function(compile) {
    return {
        restrict: 'A',
        controller: 'pages',
        scope: {
            text: '=richtextlivereplace'
        },
        link: function(scope, element) {
            scope.variables = scope.$parent.variables;
            scope.$watch('text', function() {
                var template = scope.text;
                if (template) {
                    template = template.replace(/\\n/g, '<br/>');
                    var compiled = compile(template)(scope);
                    element.html('');
                    element.append(compiled);
                }
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
}]);
