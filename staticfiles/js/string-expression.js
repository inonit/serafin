/**
 * Angular directive for writing and evaluating
 * string expressions.
 * */

"use strict";


angular.module("stringExpression", ["autocompleteSearch"])

    .config(function($httpProvider) {
        $httpProvider.defaults.headers.common["X-Requested-With"] = "XMLHttpRequest";
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
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

                function post(url, data) {
                    QueryService.post(url, data).then(function(response) {
                        $scope.expression.response.message = "";
                        $scope.expression.response.result = response.result;
                        $scope.expression.response.preview = response.query + "=" + response.result;
                    }, function(reason) {
                        $scope.expression.response.message = reason;
                    });
                }

                $scope.addQuery = function(url) {
                   if (ExpressionValidatorService.isValid($scope.expression.query)) {
                       QueueService.add(_.partial(post, url, $scope.expression));
                   } else if (!$scope.expression.query.length) {
                       $scope.expression.response.result = "";
                   }
                };

                $scope.expression = {
                    query: "",
                    response: {
                        result: "",
                        preview: "",
                        message: ""
                    }
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
            if (expressionString.length >= 3) {
                return true;
            }
            return false;
        }

        return {
            isValid: isValid
        }

    });