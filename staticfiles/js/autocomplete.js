/**
 * Angular module for autocompleting stuff.
 * */

"use strict";

var xhrWait = 200,
    minCharacters = 2,
    resultLimit = 20;

angular.module("autocompleteSearch", [])

    .config(function($httpProvider) {
        $httpProvider.defaults.headers.common["X-Requested-With"] = "XMLHttpRequest";
    })

    .controller("autocompleteController", function($scope, $q, $http, QueryService, QueueService) {

        QueueService.configure({timeout: xhrWait});

        function fetch(endpoint, queryString) {
            QueryService.fetch(endpoint, queryString).then(function(response) {
                // TODO: Must be able to append to existing results
                $scope.results = response;
            });
        }

        // Container for autocomplete results
        $scope.results = [];

        $scope.queryString = {
            query: "",          // Bind this one to the input field.
            limit: resultLimit
        };

        // Keep track of the currently selected item
        $scope._selectedItem = {};
        $scope.setSelectedItem = function(item) {
            $scope._selectedItem = item;
        };
        $scope.getSelectedItem = function() {
            return $scope._selectedItem;
        };

        $scope.addQuery = function(endpoint) {
            // TODO: cancel pending requests in QueueService
            if ($scope.queryString.query.length >= minCharacters) {
                QueueService.add(_.partial(fetch, endpoint, $scope.queryString));
            } else if (!$scope.queryString.query.length) {
                $scope.results = [];
            }
        }
    })

    .directive("autocompleteChoices", function($timeout, $compile) {
        /**
         * Directive for autocompleting variables into a select widget.
         * */
        return {
            restrict: "A",
            transclude: true,
            require: "?ngModel",
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

                $scope.getSelectedItem = $scope.$parent.getSelectedItem;
                $scope.setSelectedItem = function(item) {
                    // TODO: Set focus back on parents input field when selected.
                    $timeout(function() {
                        $scope.$parent.setSelectedItem(item);
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

                $scope.$watch("results", function(newInstance, oldInstance) {
                    $scope.setVisibility($scope.results.length ? true : false);
                    if (newInstance !== oldInstance) {
                        $scope.setSelectedIndex(-1);
                    }
                }, true);

            }],
            link: function($scope, $element, attrs) {

            }
        }
    })

    /**
     * Services
     * */
    .factory("QueryService", function($q, $http) {
        /**
         * Service responsible for querying the requested endpoint
         * and return a $http promise.
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