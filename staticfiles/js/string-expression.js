/**
 * Angular directive for writing and evaluating
 * string expressions.
 * */

"use strict";


angular.module("stringExpression", ["autocompleteSearch"])

    .config(function($httpProvider) {
        $httpProvider.defaults.headers.common["X-Requested-With"] = "XMLHttpRequest";
    })

    .directive("stringExpression", function() {
        return {
            restrict: "E",
            replace: true,
            transclude: false,
            require: "?ngModel",
            scope: {
                url: "@url"
            },
            templateUrl: "template/string-expression.html",
            controller: ["$scope", "$timeout", "ExpressionValidatorService", "QueryService", "QueueService",
                function($scope, $timeout, ExpressionValidatorService, QueryService, QueueService) {

                QueueService.configure({timeout: 200});

                function fetch(url, queryString) {
                    QueryService.fetch(url, queryString).then(function(response) {
                        $scope.expression.response = response;
                    })
                }

                $scope.addQuery = function(url) {
                   if (ExpressionValidatorService.isValid($scope.expression.query)) {
                       QueueService.add(_.partial(fetch, url, $scope.expression.query));
                   } else if (!$scope.expression.query.length) {
                       $scope.expression.response = {};
                   }
                };

                $scope.expression = {
                    query: "",
                    response: {}
                };
            }],
            link: function(scope, element, attrs) {
                var input = element.children("input[type=text]");
            }
        }
    })

    .service("ExpressionValidatorService", function() {

        function isValid(expressionString) {
            /* Implement some kind of client side validation
             * before posting to the server.
             * */

            return true;
        }

        return {
            isValid: isValid
        }

    });