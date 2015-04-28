/**
 * Angular directive for writing and evaluating
 * string expressions.
 * Note: The popover syntax helper requires bootstrap-popover.js and jQuery to be loaded.
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
            restrict: "AE",
            replace: true,
            transclude: true,
            require: "?ngModel",
            scope: {
                url: "@url",
                model: "=ngModel",
                placeholder: "@placeholder",
                headerTitle: "@headerTitle",
                popoverTitle: "@popoverTitle",
                popoverTemplate: "@popoverTemplate",
                popoverPlacement: "@popoverPlacement"
            },
            template:
                '<div class="expression-widget-wrapper">' +
                '  <input type="text" placeholder="{{ placeholder }}"' +
                '      ng-model="expression.query"' +
                '      ng-change="addQuery(\'{{ url }}\')">' +
                '    <div class="preview-box">' +
                '      <div class="header">' +
                '        <span class="title">{{ headerTitle }}</span>' +
                '        <div class="ctrl right">' +
                '          <i class="icon-question-sign"' +
                '              popover-placement="{{ popover.placement }}" popover="{{ popover.content }}"></i>' +
                '        </div>' +
                '        </div>' +
                '        <div class="validator">' +
                '          <p class="expression">' +
                '            <span>{{ expression.preview }}</span>' +
                '          </p>' +
                '          <p class="validation-message" ng-if="expression.response.reason">' +
                '            <span>{{ expression.response.reason }}</span>' +
                '          </p>' +
                '        </div>' +
                '      </div>' +
                '   </div>',
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

                function getVariableTokens(searchString) {
                    /**
                     * Identifies variables from the searchString.
                     * Returns an array of variables (without the $prefix).
                     * */
                    var re = /(?:^|\W)\$(\w+)(?!\w)/g, match, matches = [];
                        while (match = re.exec(searchString)) {
                          matches.push(match[1]);
                        }
                    return matches;
                }

                $scope.expression = {
                    query: $scope.model,
                    preview: "",
                    response: {
                        result: "",
                        reason: ""
                    }
                };

                $scope.addQuery = function (url) {
                    if (ExpressionValidatorService.isValid($scope.expression.query)) {
                        QueueService.add(_.partial(post, url, $scope.expression));
                    } else if (!$scope.expression.query.length) {
                        $scope.expression.preview = $scope.expression.response.result = $scope.expression.response.reason = "";
                    }
                };

                $scope.$watch("expression.query", function(value) {
                    $scope.model = value;
                    /*
                    var variables = getVariableTokens(value);
                    if (variables.length) {
                        console.log(getVariableTokens(value));
                    }
                    */
                });

                $scope.$watch("expression.response", function(newInstance, oldInstance) {
                    if (newInstance !== oldInstance) {
                        $scope.expression.preview = $scope.expression.query + " = " + newInstance.result;
                    }
                });
            }],
            link: function(scope, element, attrs) {
                var toggleHelp = element.find('i[class="icon-question-sign"]'),
                    contentTemplate = $compile($templateCache.get(scope.popoverTemplate))(scope);

                $(toggleHelp).popover({
                    html: true,
                    placement: scope.popoverPlacement,
                    title: scope.popoverTitle,
                    content: contentTemplate
                });

                // TODO: If model has initial value, post and evaluate it.
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