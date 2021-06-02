const serafin = angular.module('serafin', []);

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
    scope.dead_end = true;
    scope.loaded = false;

    if (api) {
        var url = api + window.location.search;

        http.get(url).then(response => {
            scope.error = null;
            scope.getVariables(response.data.data);
            scope.title = response.data.title;
            scope.page = response.data.data;
            scope.dead_end = response.data.dead_end;
            scope.stacked = response.data.stacked;
            scope.is_back = response.data.is_back;
            scope.page_id = response.data.page_id;
            scope.read_only = response.data.read_only;
            scope.loaded = true;
        }, reason => {
            scope.error = reason.data;
            scope.page = {};
            scope.loaded = true;
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
                    if (field.field_type == 'phone') {
                        data[field.variable_name] = scope.variables[field.variable_name]
                    }
                    else {
                        data[field.variable_name] = field.value
                    }
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


    scope.back = function () {
        if (!scope.read_only && $("form .ng-dirty").length > 0) {
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

serafin.directive('internationalPhone', ['$rootScope', function (rootScope) {
    return {
        restrict: 'A',
        require: '^ngModel',
        scope: {
          ngModel: '=',
          country: '='
        },
        link: function (scope, element, attrs, ctrl) {
            var iti = window.intlTelInput(element[0], {
                initialCountry: "auto",
                geoIpLookup: function(success, failure) {
                    var meta = document.createElement('meta');
                    meta.name = "referrer";
                    meta.content = "no-referrer";
                    document.getElementsByTagName('head')[0].appendChild(meta);
                    $.get("https://ipinfo.io/json", function() {}).always(function(resp) {
                        var countryCode = (resp && resp.country) ? resp.country : "";
                        success(countryCode);
                        document.getElementsByTagName('head')[0].removeChild(meta);
                    });
                }
            });

            ctrl.$validators.phone = function(modelValue, viewValue) {
                if (viewValue != '' || modelValue != '') {
                    return iti.isValidNumber();
                }
                return true;
            };

            scope.$watch(function () {
                if (ctrl.$modelValue !== undefined) {
                    iti.setNumber(ctrl.$modelValue);
                }
                return ctrl.$modelValue;
            }, function (newVal) {
                var number = iti.getNumber(intlTelInputUtils.numberFormat.E164);
                if (!number) number = '';
                rootScope.variables[scope.$parent.field.variable_name] = number;
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

    const bulletColorHandling = function (html) {
        var root = $("<div>").append($(html));

        $(root).find("ul,ol").each(function() {
            var color = $(this).find('span:first').css("color");
            var direction = $(this).find('li:first').css("direction");
            if (color !== undefined) {
                $(this).css("color", color);
            }
            if (direction !== undefined) {
                $(this).css("direction", direction);
            }
        });
        return root.html();
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
                    template = bulletColorHandling(template);
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

const portal = angular.module('portal', []);

portal.config(['$httpProvider', function (httpProvider) {
    httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    httpProvider.defaults.headers.post['X-CSRFToken'] = csrf_token;
    if (!httpProvider.defaults.headers.get) {
        httpProvider.defaults.headers.get = {};
    }
    // disable IE AJAX request caching
    httpProvider.defaults.headers.get['If-Modified-Since'] = '0';
}]);

portal.directive('dynamicTextSize', function () {
    return {
        restrict: 'A',
        link: function (scope, element, attrs) {

            function updateFontSize(textLength) {
                if (textLength > 0) {
                    $(element).css("font-size", "8vmin");
                }
                if (textLength > 20) {
                    $(element).css("font-size", "7vmin");
                }
                if (textLength > 30) {
                    $(element).css("font-size", "6vmin");
                }
                if (textLength > 40) {
                    $(element).css("font-size", "5vmin");
                }
            }


            scope.$watch('current_page_title', function (newValue, oldValue, scope, element) {
                if (newValue !== undefined) {
                    let valueSize = newValue.length;
                    updateFontSize(valueSize);
                }
            });
        }
    };
});

portal.controller('portal', ['$scope', '$http', function (scope, http) {

}]);

portal.controller('modules', ['$scope', '$http', function (scope, http) {

}]);


var generalConfig = function() {
    return function (httpProvider) {
    httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    httpProvider.defaults.headers.post['X-CSRFToken'] = csrf_token;
    if (!httpProvider.defaults.headers.get) {
        httpProvider.defaults.headers.get = {};
    }
    // disable IE AJAX request caching
    httpProvider.defaults.headers.get['If-Modified-Since'] = '0';

    }
};




const idle = angular.module('idle', ['ngIdle']);

idle.controller('idle', function ($scope, $timeout, Idle) {
    $scope.events = [];

    var onIdle = false;

    $scope.stay_loggedin = function() {
        $("#idleModal").hide();
        onIdle = false;
    };

    $scope.logout = function() {
        window.location.href = '/logout';
    };

    $scope.$on('IdleStart', function() {
        if (!onIdle) {
            onIdle = true;
            $scope.countdown = Idle.getTimeout();
            $scope.$apply();
            var timeoutFunc = function () {
                if (!onIdle) {
                    return;
                }
                console.log("counter");
                $scope.countdown = $scope.countdown - 1;
                $scope.$apply();
                if ($scope.countdown == 0) {
                    $scope.logout();
                } else {
                    $timeout(timeoutFunc, 1000);
                }
            };
            $timeout(timeoutFunc, 1000);
            $("#idleModal").show();
        }
    });

    $scope.$on('IdleTimeout', function() {
        $scope.logout();
    });

});

idle.config(function(IdleProvider, KeepaliveProvider) {
	IdleProvider.idle(15*60); // in seconds
	IdleProvider.timeout(60); // in seconds
	KeepaliveProvider.interval(3); // in seconds
});

idle.run(function(Idle){
	// start watching when the app runs. also starts the Keepalive service by default.
	Idle.watch();
});

if (window.jQuery) {
    $(window).on("click", function (e) {
        if (e.target == null || e.target.parentElement == null) {
            return;
        }

        if ((e.target.classList.contains("menu-icon") ||
            e.target.parentElement.classList.contains("menu-icon"))) {
            $(".header-tabs").show();
        }

        if ((e.target.classList.contains("mobile-close") ||
            e.target.parentElement.classList.contains("mobile-close"))) {
            $(".header-tabs").removeAttr("style");
        }


        if ((e.target.classList.contains("header-user") || e.target.parentElement.classList.contains("header-user"))
            && $(".header-user-menu").css('display') == 'none') {
            $(".header-user-menu").show();
        } else {
            $(".header-user-menu").hide();
        }

        if ((e.target.classList.contains("episodes-menu-title-mobile") || e.target.parentElement.classList.contains("episodes-menu-title-mobile"))
            && $(".episodes-menu").css('display') == 'none') {
            $(".episodes-menu").show();
        } else {
            if ($(".page").css("display") !== "flex") {


                $(".episodes-menu").hide();
                $(".page").show();
            }
        }

        if ((e.target.classList.contains("episodes-link") || e.target.parentElement.classList.contains("episodes-link"))
            && $(".episodes-menu").css('display') == 'none') {
            $(".episodes-menu").show();
            $(".page").hide();
        } else {
            if ($(".page").css("display") !== "flex") {
                $(".episodes-menu").hide();
            }
        }

    });
}