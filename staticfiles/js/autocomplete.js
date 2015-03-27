/**
 * Angular module for autocompleting stuff.
 * Requires lodash to be loaded (Could probably be avoided by rewriting some stuff,
 * it was just convenient for me =))
 * */

"use strict";

var xhrWait = 200,
    minCharacters = 3,
    resultLimit = 20;

angular.module("autocompleteSearch", [])

    .config(function($httpProvider) {
        $httpProvider.defaults.headers.common["X-Requested-With"] = "XMLHttpRequest";
    })

    .controller("autocompleteController", function($scope, QueryService, QueueService) {

        QueueService.configure({timeout: xhrWait});

        function fetch(endpoint, queryString) {
            QueryService.fetch(endpoint, queryString).then(function(response) {
                $scope.results = response;
            });
        }

        $scope.results = [];
        $scope.queryString = {
            query: "",                  // Bind this one to the input field.
            limit: resultLimit
        };

        $scope.addQuery = function(endpoint) {
            // TODO: Should cancel current request so we don't send a request for each character written.
            if ($scope.queryString.query.length >= minCharacters) {
                QueueService.add(_.partial(fetch, endpoint, $scope.queryString));
            } else if (!$scope.queryString.query.length) {
                $scope.results = [];
            }
        };
    })

    .directive("autocompleteChoices", function($timeout) {
        /**
         * Directive for autocompleting variables into a custom "select" widget
         * (actually just a div with some spans in it).
         * */
        return {
            restrict: "A",
            require: "?ngModel",
            transclude: true,
            scope: {
                results: "=ngModel",
                _isVisible: "=ngShow"
            },
            template:
                '<span ng-repeat="item in results track by $index" ' +
                    'ng-click=setSelectedItem(item) ' +
                    'ng-class="{active: ($index === getSelectedIndex())}" ' +
                    'ng-mouseenter="setSelectedIndex($index)" ' +
                    'data-id="{{ item.id }}" ' +
                    'class="autocomplete-item">' +
                        '{{ item.name }}' +
                '</span>',
            controller: ["$scope", function($scope) {

                $scope._selectedIndex = -1;
                $scope.getSelectedIndex = function() {
                    return $scope._selectedIndex;
                };
                $scope.setSelectedIndex = function(n) {
                    $timeout(function() {
                        $scope._selectedIndex = parseInt(n);
                    });
                };

                $scope._selectedItem = {};
                $scope.getSelectedItem = function() {
                    return $scope._selectedItem;
                };
                $scope.setSelectedItem = function(item) {
                    $timeout(function() {
                        $scope._selectedItem = item;
                        $scope.$parent.queryString.query = item.name;
                        $scope.setVisibility(false);
                    });
                };

                $scope._isVisible = false;
                $scope.setVisibility = function(bool, delay) {
                    delay = parseInt(delay) || 0;
                    if (_.isBoolean(bool)) {
                        $timeout(function() {
                            $scope._isVisible = bool;
                        }, delay, true);
                    }
                };

                $scope.keys = [];
                $scope.keys.push({code: 27, action: function() { $scope.setVisibility(false); }});
                $scope.keys.push({code: 13, action: function() {
                    $scope.setSelectedItem($scope.results[$scope.getSelectedIndex()]);
                }});
                $scope.keys.push({code: 38, action: function() {
                    $scope.setVisibility(true);
                    $scope.setSelectedIndex($scope._selectedIndex > 0 ? $scope._selectedIndex - 1 : $scope.results.length - 1);
                }});
                $scope.keys.push({code: 40, action: function() {
                    $scope.setVisibility(true);
                    $scope.setSelectedIndex($scope._selectedIndex < $scope.results.length - 1 ? $scope._selectedIndex + 1 : 0);
                }});

                $scope.$on("keydown", function(_, obj) {
                    var code = obj.code;
                    $scope.keys.forEach(function(o) {
                        if (o.code !== code) {
                            return;
                        }
                        o.action();
                        $scope.$apply();
                    });
                });

                $scope.$watch("results", function(newInstance, oldInstance) {
                    $scope.setVisibility($scope.results.length ? true : false);
                    if (newInstance !== oldInstance) {
                        $scope.setSelectedIndex(-1);
                    }
                }, true);

            }],
            link: function(scope, element, attrs) {
                var input = element.parent().children("input[type=text]");
                input.bind("keydown", function(e) {
                    if (_.find(scope.keys, "code", e.keyCode)) {
                        e.preventDefault();
                        scope.$broadcast("keydown", {code: e.keyCode});
                    }
                });

                input.bind("click", function(e) {
                    if (scope.results.length) {
                        scope.setVisibility(true);
                    }
                });

                input.bind("blur", function(e) {
                    scope.setVisibility(false);
                });
            }
        }
    })

    /**
     * Services
     * */
    .factory("QueryService", function($q, $http) {
        /**
         * Service responsible for querying the requested endpoint
         * and return a promise.
         * */
        return {
            fetch: function(endpoint, queryString) {
                var deferred = $q.defer();
                $http({
                    method: "GET",
                    url: endpoint,
                    params: queryString
                })
                .success(function(response, status) {
                    deferred.resolve(response);
                })
                .error(function(reason) {
                    deferred.reject(reason);
                });
                return deferred.promise;
            }
        };
    })
    .factory("QueueService", function($log, $timeout) {
        /**
         * Async queue shamlessly stolen from
         * http://blog.itcrowd.pl/2014/04/queueing-service-for-angularjs.html
         * */
        var queueName = "default",
            queue = [],
            QueueConfig = {};

        QueueConfig[queueName] = {timeout: 0};

        function isDuplicate(item, callback, options) {
            if (null != options.groupId || null != item.options.groupId) {
                return options.groupId === item.options.groupId;
            }
            return item.callback === callback;
        }

        function createQueueItem(callback, config, options) {
            config = angular.extend({}, config, options);

            var promise = $timeout(callback, config.timeout);
            promise.then(function removeQueueItem() {
                for (var i = 0; i < queue.length; i++) {
                    if (queue[i].promise === promise) {
                        queue.splice(i, 1);
                        return;
                    }
                }
            });
            return {
                callback: callback,
                options: options,
                promise: promise
            };
        }

        function add(callback, options) {
            options = angular.extend({queueId: queueName}, options);

            for (var i = 0; i < queue.length; i++) {
                if (isDuplicate(queue[i], callback, options)) {
                    $timeout.cancel(queue[i].promise);
                    queue.splice(i, 1);
                    break;
                }
            }

            if (null == QueueConfig[options.queueId]) {
                $log.warn("No queue `" + options.queueId + "` defined");
                options.queueId = queueName;
            }

            var config = angular.extend({}, QueueConfig[options.queueId], options);
            if (config.timeout > 0) {
                queue.push(createQueueItem(callback, config, options));
            } else {
                callback();
            }
        }

        function configure(config, queueId) {
            if (null == queueId) {
                queueId = queueName;
            }
            QueueConfig[queueId] = angular.extend(QueueConfig[queueId] || {}, config);
        }
        return {
            add: add,
            configure: configure
        };
    });