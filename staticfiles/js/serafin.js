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
        if (!scope.read_only && $("form .ng-dirty").length > 0) {
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

    scope.increaseTextLengthWorkaround = increaseTextLengthWorkaround;
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
        if (value === undefined || value === null) {
            return;
        }
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

    const increaseHtmlTextLengthWorkaround = function (html) {
        let jHtml = $(html);
        for (let i = 0; i < jHtml.contents().length; i++) {
            if (jHtml.contents().eq(i).text().search(spaceBetweenCharacters) > -1) {
                let content = jHtml.contents().eq(i).html();
                content = increaseTextLengthWorkaround(content);
                jHtml.contents().eq(i).html(content);
            }
        }
        return $("<div />").append(jHtml).clone().html();
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
                    template = bulletColorHandling(template);
                    template = increaseHtmlTextLengthWorkaround(template);
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

portal.run(['$rootScope', '$http', function (scope, http) {
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
            scope.loaded = true;

            // switch cover image
            if (scope.cover_image != null) {
                let bg = $(".home-image").css("background-image");
                $(".home-image").css("background-image", "url(\"" + scope.cover_image + "\")")
            }

        }, reason => {
            scope.error = reason.data;
            scope.page = {};
            scope.loaded = true;
        });
    }

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
                if (newValue !== undefined && newValue !== null) {
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

const therapistapp = angular.module('therapistapp', ['ngEmojiPicker']);

therapistapp.config(['$httpProvider', generalConfig()]);

therapistapp.run(['$rootScope', '$http', function (scope, http) {

    scope.user_pages = [];
    scope.display_show_table = true;

    if (api) {
        http.get(api).then(response => {
            scope.error = null;
            scope = Object.assign(scope, response.data);
            if (window.location.search.indexOf("user_id") >= 0) {
                scope.userstat(window.location.search.substr(
                    window.location.search.indexOf("=") + 1,
                    window.location.search.length - 1))
            }
        }, reason => {
            scope.error = reason.data;
            scope.page = {};
        });
    }

}]);

if (typeof(ChatController) !== 'undefined') {
    therapistapp.controller('ChatController', ['$scope', '$http', '$httpParamSerializerJQLike', '$timeout', '$interval', ChatController()]);
    therapistapp.directive('fileModel', ['$parse', FileModelDirective()]);
    therapistapp.directive('html5afix', FixAudioSrcDirective());
}

therapistapp.controller('therapist', ['$rootScope', '$scope', '$http', '$httpParamSerializerJQLike', '$timeout', '$interval', function (rootScope, scope, http, httpParamSerializerJQLike, timeout, interval) {

    var loadResponse = function (response) {
        scope.selectedTransformationVariable = null;
        scope.transofrmationTable = null;
        scope.user_pages = response.data.pages;
        scope.user_id = response.data.id;
        scope.variables = response.data.variables;
        scope.notifications = response.data.notifications;
        scope.has_messages = response.data.has_messages;
        scope.notes = response.data.notes;
        scope.allow_chat = response.data.allow_chat;

        scope.variablesForm = {
            fields: [],
            data: {}
        };
        scope.variables.forEach(function (variable) {
            if (variable.editable) {
                scope.variablesForm.fields.push({'name': variable.name, 'value': variable.value, 'display': variable.display_name,
                'options': variable.options});
                scope.variablesForm.data[variable.name] = variable.value;
            }
        });
        scope.notifications_icon = false;
        scope.notifications.forEach(function (notification) {
            scope.notifications_icon = scope.notifications_icon || !notification.is_read;
            notification['time_display'] = moment(notification.timestamp).calendar();
        });
    };
    scope.selectedTransformationVariable = '';

    scope.showAllUsers = function() {
        scope.display_show_table=true;
        $("#nav-user-pages-tab").click();
        scope.stop_chat();

        if (api) {
            http.get(api + window.location.search).then(response => {
            scope.error = null;
            scope = Object.assign(scope, response.data);
        }, reason => {
            scope.error = reason.data;
            scope.page = {};
        });
    }
    };

    scope.updateTransformationTable = function () {
        let selectedVariable = scope.variables.find(elem => elem.name == scope.selectedTransformationVariable);
        scope.transofrmationTable = selectedVariable.values;
    };

    scope.markNotificationRead = function(notificationId) {
        let notification = scope.notifications.find(elem => elem.id == notificationId);
        if (notification.is_read) {
            return;
        }
        var url = api + '?user_id=' + scope.user_id;
        http({
            url: url,
            method: 'POST',
            data: httpParamSerializerJQLike({'notification_id': notificationId}),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }).then(function (response) {
            loadResponse(response);
        });
        scope.notifications_icon = false;
        scope.notifications.forEach(function (notification) {
            if (notification.id == notificationId) {
                notification.is_read = true;
            }
            scope.notifications_icon = scope.notifications_icon || !notification.is_read;
        });
    };

    scope.addNote = function() {
        if (scope.new_note == null || scope.new_note.trim() == '') {
            return;
        }

        var url = api + '?user_id=' + scope.user_id;
        http({
            url: url,
            method: 'POST',
            data: httpParamSerializerJQLike({'note_msg': scope.new_note}),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        }).then(function (response) {
            scope.new_note = '';
            loadResponse(response);
        });

    };

    scope.convertTime = function(time) {
        return moment(time).calendar();
    };

    scope.showMoreGoldVariables = function (element) {
        debugger;
    };

    rootScope.userstat = function (user_id) {
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
    };

    scope.$watch('$viewContentLoaded', function () {
        console.log('$viewContentLoaded');
    });

    scope.start_chat = function () {
        scope.$broadcast('startChat');
    };

    scope.stop_chat = function () {
        scope.$broadcast('stopChat');
    };

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

const mytherapistapp = angular.module('mytherapist', ['ngEmojiPicker']);
mytherapistapp.config(['$httpProvider', generalConfig()]);
if (typeof(ChatController) !== 'undefined') {
    mytherapistapp.controller('ChatController', ['$scope', '$http', '$httpParamSerializerJQLike', '$timeout', '$interval', ChatController()]);
    mytherapistapp.directive('fileModel', ['$parse', FileModelDirective()]);
    mytherapistapp.directive('html5afix', FixAudioSrcDirective());
}

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

const spaceBetweenCharacters = /(?<=\S)\s+(?!(\s|$))/;
const increaseTextLengthWorkaround = function (text) {
        let space_idx = text.search(spaceBetweenCharacters);
        if (space_idx > -1) {
            return text.slice(0, space_idx) + ' '.repeat(250) + text.slice(space_idx);
        }
        return text;
};
