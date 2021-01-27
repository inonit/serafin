/**
 * Angular directive for writing and evaluating
 * string expressions.
 * Note: The popover syntax helper requires bootstrap-popover.js and jQuery to be loaded.
 * */

"use strict";


angular.module("stringExpression", ["autocompleteSearch", "mentio"])

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
                '  <input id="expression-input" type="text" autocomplete="off" placeholder="{{ placeholder }}"' +
                '      ng-model="expression.query"' +
                '      ng-change="addQuery(\'{{ url }}\')"' +
                '      mentio' +
                '      mentio-trigger-char="\'$\'"' +
                '      mentio-search="getVariable(term)"' +
                '      mentio-select="getVariableText(item)"' +
                '      mentio-items="variables"' +
                '      mentio-template-url="template/expression-variables.html">' +
                '    <div class="preview-box">' +
                '      <div class="header">' +
                '        <span class="title">{{ headerTitle }}</span>' +
                '        <div class="ctrl right">' +
                '          <i class="fa fa-question"' +
                '              popover-placement="{{ popover.placement }}" popover="{{ popover.content }}"></i>' +
                '        </div>' +
                '        </div>' +
                '        <div class="validator">' +
                '          <span class="expression">{{ expression.query }}</span>' +
                '          <p class="result" ng-if="expression.response.result !== null">' +
                '            <span>{{ expression.response.result }}</span>' +
                '          </p>' +
                '          <p class="validation-message" ng-if="expression.response.reason">' +
                '            <span>{{ expression.response.reason }}</span>' +
                '          </p>' +
                '        </div>' +
                '      </div>' +
                '   </div>',
            controller: ["$scope", "$timeout", "$filter", "ExpressionValidatorService", "QueryService", "QueueService",
                function($scope, $timeout, $filter, ExpressionValidatorService, QueryService, QueueService) {

                QueueService.configure({timeout: 200});

                function pythonizeResult(response) {
                    if (response.result === true)
                        response.result = 'True'
                    else if (response.result === false)
                        response.result = 'False'
                    else if (typeof response.result === 'string')
                        response.result = '"' + response.result + '"';
                    return response
                }

                function post(url, data) {
                    QueryService.post(url, data).then(function(response) {
                        $scope.expression.response = pythonizeResult(response.response);
                    }, function(reason) {
                        $scope.expression.response.result = null;
                        $scope.expression.response.reason = reason;
                    });
                }

                function queryVariables(url, data) {
                    QueryService.get(url, data).then(function(response) {
                        $scope.variables = response;
                    }, function() {
                        $scope.variables = [];
                    });
                }

                var variables = [];
                $scope.expression = {
                    query: $scope.model,
                    response: {
                        result: null,
                        reason: null
                    }
                };

                $scope.addQuery = function (url) {
                    if (ExpressionValidatorService.isValid($scope.expression.query)) {
                        QueueService.add(_.partial(post, url, $scope.expression));
                    } else if (!$scope.expression.query.length) {
                        $scope.expression.response.result = $scope.expression.response.reason = null;
                    }
                };

                $scope.getVariable = function(term) {
                    /**
                     * Search the API for variable names
                     * */
                    var url = "/api/system/variables/search/",
                        query = {query: term};
                    QueueService.add(_.partial(queryVariables, url, query));
                };

                $scope.getVariableText = function(item) {
                    return "$" + item.name;
                };

                $scope.$watch("expression.query", function(value) {
                    $scope.model = value;
                });

                if ($scope.expression.query)
                    $scope.addQuery($scope.url);
            }],
            link: function(scope, element, attrs) {
                var toggleHelp = element.find('i.fa-question'),
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

    .directive("bootstrapTooltip", function() {
        return {
            restrict: "A",
            scope: {
                tooltipTitle: "=tooltipTitle",
                tooltipPlacement: "@tooltipPlacement"
            },
            link: function(scope, element, attrs) {
                $(element).tooltip({
                    container: "body",
                    title: scope.tooltipTitle,
                    placement: scope.tooltipPlacement || "top"
                });
                element.bind("mouseenter", function(e) {
                    $(element).tooltip("show");
                });
                element.bind("mouseleave", function(e) {
                    $(element).tooltip("hide");
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
