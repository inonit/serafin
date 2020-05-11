var serafin = angular.module('serafin', []);

serafin.config(['$httpProvider', function (httpProvider) {
    httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    httpProvider.defaults.headers.post['X-CSRFToken'] = csrf_token;
    if (!httpProvider.defaults.headers.get) {
        httpProvider.defaults.headers.get = {};
    }
    // disable IE AJAX request caching
    httpProvider.defaults.headers.get['If-Modified-Since'] = '0';
}]);

serafin.run(['$rootScope', '$http', function (scope, http) {
    scope.title = '...';
    scope.page = {};
    scope.variables = {};

    if (api) {
        var url = api + window.location.search;
        if (module_id) {
            url = '/module/' + module_id;
        }

        http.get(url).then(response => {
            scope.error = null;
            scope.getVariables(response.data.data);
            scope.title = response.data.title;
            scope.page = response.data.data;
            scope.dead_end = response.data.dead_end;
            scope.stacked = response.data.stacked;
            scope.is_chapter = response.data.is_chapter;
            scope.chapters = response.data.chapters;
            scope.is_back = response.data.is_back;
            scope.page_id = response.data.page_id;
            scope.read_only = response.data.read_only;
        }, reason => {
            scope.error = reason.data;
            scope.page = {};
        });
    }

    scope.$on('title', function (event, data) {
        scope.title = data;
    });

    scope.getVariables = function (data) {
        data.forEach(function (pagelet) {
            for (var variableName in pagelet.variables) {
                scope.variables[variableName] = pagelet.variables[variableName];
            }
        });
    }
}]);

serafin.controller('pages', ['$scope', '$http', function (scope, http) {
    var timerStart = new Date();

    var read_form_data = function () {
        var data = {};
        scope.page.forEach(function (pagelet) {
            if (pagelet.content_type == 'form' ||
                pagelet.content_type == 'quiz') {
                pagelet.content.forEach(function (field) {
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

    scope.next = function () {
        scope.form.submitted = true;
        if (scope.form.$invalid) {
            return;
        }

        var data = read_form_data();
        var timerEnd = new Date();
        var timeSpent = timerEnd.getTime() - timerStart.getTime();
        data.timer = timeSpent;

        var url = (scope.dead_end && scope.stacked ? api + '?pop=1' : api + '?next=1');
        if (scope.read_only) {
            url = api + "?back=" + scope.page_id;
            data = {};
        }
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
            scope.is_back = response.data.is_back;
            scope.page_id = response.data.page_id;
            scope.form.submitted = false;
            scope.read_only = response.data.read_only;
            window.scrollTo(0, 0);
        }, reason => {
            scope.error = reason.data;
            scope.page = {};
        });
    };

    scope.chapter_url = function (chapter_id) {
        if (!scope.read_only && $("form .ng-not-empty").length > 0) {
            var answer = confirm(areYouSure);
            if (!answer) {
                return;
            }
        }
        var timerEnd = new Date();
        var timeSpent = timerEnd.getTime() - timerStart.getTime();
        var data = {'timer': timeSpent}

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
            scope.read_only = response.data.read_only;
            scope.is_back = response.data.is_back;
            scope.page_id = response.data.page_id;
            scope.form.submitted = false;
            window.scrollTo(0, 0);
        }, reason => {
            scope.error = reason.data;
            scope.page = {};
        });
    }

    scope.back = function () {
        if (!scope.read_only && $("form .ng-not-empty").length > 0) {
            var answer = confirm(areYouSure);
            if (!answer) {
                return;
            }
        }
        var timerEnd = new Date();
        var timeSpent = timerEnd.getTime() - timerStart.getTime();
        var data = {'timer': timeSpent};

        var url = (api + '?back=-' + scope.page_id);
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
            scope.read_only = response.data.read_only;
            scope.is_back = response.data.is_back;
            scope.page_id = response.data.page_id;
            scope.form.submitted = false;
            window.scrollTo(0, 0);
        }, reason => {
            scope.error = reason.data;
            scope.page = {};
        });

    }
}]);

serafin.directive('page', function () {
    return {
        restrict: 'C',
        link: function (scope, element, attrs) {
            if (scope.form) {
                scope.form.submitted = false;
            }
            ;
        }
    };
});

serafin.directive('checkboxlist', function () {
    return {
        restrict: 'A',
        link: function (scope, element, attrs, ngModel) {

            var clScope = scope.$parent.$parent;

            if (clScope.field && clScope.field.required) {
                clScope.subForm.$setValidity(
                    'required',
                    clScope.field.value.length > 0
                )
            }

            scope.toggle = function (list, item) {
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

            scope.$watch('alt.selected', function (newVal, oldVal) {
                if (newVal) {
                    scope.pagelet.content.text = scope.alt.text;
                } else {
                    scope.pagelet.content.text = '';
                }
            });
        }
    }
});

serafin.directive('title', function () {
    return {
        restrict: 'CE',
        link: function (scope, element, attrs) {
            scope.$watch('title', function (newVal, oldVal) {
                if (newVal !== oldVal) {
                    element.text(scope.title);
                }
            });
        }
    };
});

serafin.directive('liveinput', ['$rootScope', function (rootScope) {
    return {
        restrict: 'A',
        require: 'ngModel',
        link: function (scope, element, attrs, ngModel) {
            scope.$watch(function () {
                return ngModel.$modelValue;
            }, function (newVal) {
                if (!newVal) newVal = '...'
                rootScope.variables[scope.$parent.field.variable_name] = newVal;
            });
        }
    };
}]);

serafin.directive('stringToNumber', function () {
    return {
        require: 'ngModel',
        link: function (scope, element, attrs, ngModel) {
            ngModel.$parsers.push(function (value) {
                return '' + value;
            });
            ngModel.$formatters.push(function (value) {
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

serafin.directive('livereplace', ['$compile', function (compile) {
    return {
        restrict: 'A',
        controller: 'pages',
        scope: {
            text: '=livereplace',
        },
        link: function (scope, element, attrs) {
            scope.variables = scope.$parent.variables;
            scope.$watch('text', function () {
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

serafin.directive('richtextlivereplace', ['$compile', function (compile) {

    const floatImageHandling = function (html) {
        return html;
    };

    return {
        restrict: 'A',
        controller: 'pages',
        scope: {
            text: '=richtextlivereplace'
        },
        link: function (scope, element) {
            scope.variables = scope.$parent.variables;
            scope.$watch('text', function () {
                var template = scope.text;
                if (template) {
                    template = floatImageHandling(template);
                    var compiled = compile(template)(scope);
                    element.html('');
                    element.append(compiled);
                }
            })
        }
    };
}]);

serafin.directive('menu', ['$timeout', function (timeout) {
    return {
        restrict: 'C',
        link: function (scope, element, attrs) {
            var win = angular.element(window)
            win.on('resize', function () {
                timeout(function () {
                    scope.desktop = win[0].innerWidth > 640;
                    scope.menu = win[0].innerWidth > 640;
                });
            })
            win.triggerHandler('resize');

            scope.toggleMenu = function () {
                if (!scope.desktop) {
                    scope.menu = !scope.menu;
                }
            }
        }
    }
}]);

const newserafin = angular.module('newserafin', []);

newserafin.config(['$httpProvider', function (httpProvider) {
    httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    httpProvider.defaults.headers.post['X-CSRFToken'] = csrf_token;
    if (!httpProvider.defaults.headers.get) {
        httpProvider.defaults.headers.get = {};
    }
    // disable IE AJAX request caching
    httpProvider.defaults.headers.get['If-Modified-Since'] = '0';
}]);

newserafin.run(['$rootScope', '$http', function (scope, http) {
    scope.modules_finished = -1;
    if (typeof (modules) !== 'undefined') {
        scope.modules = modules;
    }
    if (typeof (current_module_id) !== 'undefined') {
        scope.current_module_id = current_module_id;
    }

    if (api) {
        http.get(api + window.location.search).then(response => {
            scope.error = null;
            scope = Object.assign(scope, response.data);
        }, reason => {
            scope.error = reason.data;
            scope.page = {};
        });
    }

}]);

newserafin.controller('portal', ['$scope', '$http', function (scope, http) {

}]);

newserafin.controller('modules', ['$scope', '$http', function (scope, http) {

}]);


const therapistapp = angular.module('therapistapp', []);

therapistapp.config(['$httpProvider', function (httpProvider) {
    httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    httpProvider.defaults.headers.post['X-CSRFToken'] = csrf_token;
    if (!httpProvider.defaults.headers.get) {
        httpProvider.defaults.headers.get = {};
    }
    // disable IE AJAX request caching
    httpProvider.defaults.headers.get['If-Modified-Since'] = '0';
}]);

therapistapp.run(['$rootScope', '$http', function (scope, http) {

    scope.user_pages = [];
    scope.display_show_table = true;

    if (api) {
        http.get(api + window.location.search).then(response => {
            scope.error = null;
            scope = Object.assign(scope, response.data);
        }, reason => {
            scope.error = reason.data;
            scope.page = {};
        });
    }

}]);


therapistapp.controller('therapist', ['$scope', '$http', '$httpParamSerializerJQLike', function (scope, http, httpParamSerializerJQLike) {

    var loadResponse = function (response) {
        scope.selectedTransformationVariable = null;
        scope.transofrmationTable = null;
        scope.user_pages = response.data.pages;
        scope.user_id = response.data.id;
        scope.user_email = response.data.email;
        scope.user_phone = response.data.phone;
        scope.variables = response.data.variables;
        scope.variablesForm = {
            fields: [],
            data: {}
        };
        scope.variables.forEach(function (variable) {
            if (variable.editable) {
                scope.variablesForm.fields.push({'name': variable.name, 'value': variable.value});
                scope.variablesForm.data[variable.name] = variable.value;
            }
        });
    };
    scope.selectedTransformationVariable = '';

    scope.updateTransformationTable = function () {
        let selectedVariable = scope.variables.find(elem => elem.name == scope.selectedTransformationVariable);
        scope.transofrmationTable = selectedVariable.values;
    };

    scope.showMoreGoldVariables = function (element) {
        debugger;
    };

    scope.userstat = function (user_id) {
        $('#users-table').removeClass('show');
        scope.display_show_table = false;
        var url = api + '?user_id=' + user_id;
        http.get(url).then(response => {
            loadResponse(response);
        }, reason => {
            scope.error = reason.data;
            scope.page = {};
        })
    };

    scope.postVariables = function () {
        var url = api + '?user_id=' + scope.user_id;
        var data = httpParamSerializerJQLike(scope.variablesForm.data);
        http({
            url: url,
            method: 'POST',
            data: data,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }).then(function (response) {
            loadResponse(response);
        });
    }
}]);

therapistapp.component('pageVariablesTable', {
    template:
        '<div class="table-responsive">' +
        '<table class="table table-sm">' +
        '<thead>' +
        '<tr>' +
        '<th scope="col" style="width: 25%">Date</th>' +
        '<th scope="col" ng-repeat="var in $ctrl.allVariables()">{{var}}</th>' +
        '</tr>' +
        '</thead>' +
        '<tbody>' +
        '<tr ng-repeat="date in $ctrl.allDates() track by $index" >' +
        '<th style="width: 25%" scope="row">{{date}}</th>' +
        '<td ng-repeat="innerVar in $ctrl.allVariables()">{{$ctrl.getValueForVariableInDate(date, innerVar)}}</td>' +
        '</tr>' +
        '</tbody>' +
        '</table>' +
        '</div>',

    controller: function ($scope, $element, $attrs) {
        var ctrl = this;

        ctrl.allDates = function () {
            return this.variables.map(x => x.time);
        };

        ctrl.allVariables = function () {
            var allVariables = this.variables.map(x => x.vars.map(x => x.name)).reduce((acc, curr) => acc.concat(curr));
            return [...new Set(allVariables)];
        };

        ctrl.getValueForVariableInDate = function (currentDate, currentVariable) {
            var variablesInDate = this.variables.filter(x => x.time == currentDate)[0];
            var variable = variablesInDate.vars.filter(x => x.name == currentVariable);
            if (variable.length == 0) {
                return "";
            }
            return variable[0].value;
        }

    },
    bindings: {
        variables: '<'
    }
});
