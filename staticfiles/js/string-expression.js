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

    .directive("stringExpression", function($templateCache, $compile) {
        return {
            restrict: "E",
            replace: true,
            transclude: true,
            require: "?ngModel",
            scope: {
                model: "=ngModel",
                placeholder: "@placeholder",
                headerTitle: "@headerTitle",
                popoverTitle: "@popoverTitle",
                popoverTemplate: "@popoverTemplate",
                popoverPlacement: "@popoverPlacement",
                url: "@url"
            },
            templateUrl: "template/string-expression.html",
            controller: ["$scope", "$timeout", "ExpressionValidatorService", "QueryService", "QueueService",
                function($scope, $timeout, ExpressionValidatorService, QueryService, QueueService) {

                QueueService.configure({timeout: 200});

                function post(url, data) {
                    QueryService.post(url, data).then(function(response) {
                        $scope.expression.response = response.response;
                    }, function(reason) {
                        $scope.expression.response.reason = reason;
                    });
                }

                $scope.expression = {
                    query: $scope.model,
                    preview: "",
                    response: {
                        result: "",
                        reason: ""
                    }
                };

                $scope.addQuery = function(url) {
                   if (ExpressionValidatorService.isValid($scope.expression.query)) {
                       QueueService.add(_.partial(post, url, $scope.expression));
                   } else if (!$scope.expression.query.length) {
                        $scope.expression.preview = $scope.expression.response.result = $scope.expression.response.reason = "";
                   }
                };

                $scope.$watch("expression.query", function(newInstance) {
                    $scope.model = newInstance;
                });

                $scope.$watch("expression.response", function(newInstance, oldInstance) {
                    if (newInstance.result !== oldInstance.result) {
                        $scope.expression.preview = $scope.expression.query + " = " + newInstance.result;
                    }
                });
            }],
            link: function(scope, element, attrs) {
                var toggleHelp = element.find('i[class="icon-question-sign"]');
                // Using jQuery

                var contentTemplate = $templateCache.get(scope.popoverTemplate);
                $(toggleHelp).popover({
                    html: true,
                    placement: scope.popoverPlacement,
                    title: scope.popoverTitle,
                    content: $compile(contentTemplate)(scope)
                });
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