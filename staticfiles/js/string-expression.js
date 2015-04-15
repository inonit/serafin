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
            transclude: true,
            require: "?ngModel",
            scope: {
                model: "=ngModel",
                placeholder: "@placeholder",
                headerTitle: "@headerTitle",
                popoverPlacement: "@popoverPlacement",
                url: "@url"
            },
            templateUrl: "template/string-expression.html",
            controller: ["$scope", "$timeout", "$compile", "$sce", "ExpressionValidatorService", "QueryService", "QueueService",
                function($scope, $timeout, $compile, $sce, ExpressionValidatorService, QueryService, QueueService) {

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
                $(toggleHelp).popover({
                    html: true,
                    placement: scope.popoverPlacement,
                    title: "Serafin expression syntax",
                    content:
                        /* This markup use bootstrap 2.3 syntax in order to play nice
                         * with the Suit UI in serafin admin.
                         */
                        '<div class="container-fluid">' +
                        '   <div class="row">' +
                        '       <h5>Grouping</h5>' +
                        '       <p>Expression can be grouped by putting them in <b>( )</b> parentheses.</p>' +
                        '       <br />' +
                        '       <ul class="unstyled">' +
                        '           <li><b>1 + 1 * 2 = 3 </b>because of default left to right evaluation = 1 + (1 * 2)</li>' +
                        '           <li><b>(1 + 1) * 2 = 4 </b>because of explicit right to left evaluation.</li>' +
                        '       </ul>' +
                        '   </div>' +
                        '   <div class="row">' +
                        '       <h5>Varables</h5>' +
                        '       <p>' +
                        '           Variables must be prefixed with <b>`$` like eg. $MyLittlePony</b>. ' +
                        '           Any variable myst be pre-defined and will be looked up whenever ' +
                        '           encountered. If a variable is not found, the evaluation will fail ' +
                        '           with an error message.' +
                        '       </p>' +
                        '   </div>' +
                        '   <div class="row">' +
                        '       <h5>Operators</h5>' +
                        '       <p>' +
                        '           We have two set of expression types; simple arithmetic mathematical expressions ' +
                        '           and boolean expressions. Expression evaluation between mixed types are not ' +
                        '           supported, and will either throw an error or yield incorrect or unpredictable ' +
                        '           results.' +
                        '       </p>' +
                        '       <h6>Arithmetic operators</h6>' +
                        '       <div class="span5">' +
                        '           <ul class="unstyled">' +
                        '               <li>Addition ( + )</li>' +
                        '               <li>Subtraction ( - )</li>' +
                        '               <li>Division ( / )</li>' +
                        '           </ul>' +
                        '       </div>' +
                        '       <div class="span5 offset1">' +
                        '           <ul class="unstyled">' +
                        '               <li>Multiplication ( * )</li>' +
                        '               <li>Factorisation ( ^ )</li>' +
                        '               <li>Remainder ( % )</li>' +
                        '           </ul>' +
                        '       </div>' +
                        '       <h6>Boolean operators</h6>' +
                        '       <div class="span5">' +
                        '           <ul class="unstyled">' +
                        '               <li>Equal ( == )</li>' +
                        '               <li>Not equal ( != )</li>' +
                        '               <li>Less than ( < )</li>' +
                        '               <li>Less than or equal ( <= )</li>' +
                        '               <li>Greater than ( > )</li>' +
                        '           </ul>' +
                        '       </div>' +
                        '       <div class="span5 offset1">' +
                        '           <ul class="unstyled">' +
                        '               <li>Greater than or equal ( >= )</li>' +
                        '               <li>Contains ( in )</li>' +
                        '               <li>AND ( & )</li>' +
                        '               <li>OR ( | )</li>' +
                        '           </ul>' +
                        '       </div>' +
                        '   </div>' +
                        '   <div class="alert alert-error"><h5>Boolean comparisons are not yet implemented in the backend! Do not use!</h5></div>' +
                        '   <div class="row">' +
                        '       <h5>Functions</h5>' +
                        '       <p>' +
                        '           Some basic functions are supported. Functions are applied by passing a value or ' +
                        '           an expression which returns a value to it.' +
                        '       </p>' +
                        '           <ul>' +
                        '               <li><b>round(6.34)</b> would return the value `6`</li>' +
                        '               <li><b>sin(3 * (2^4) + abs(9.23))</b> would return the value `0.6298283755944591`</li>' +
                        '           </ul>' +
                        '       <div class="span5">' +
                        '           <ul class="unstyled">' +
                        '               <li><a href="http://en.wikipedia.org/wiki/Law_of_sines" target="_blank">Sine</a> ( sin )</li>' +
                        '               <li><a href="http://en.wikipedia.org/wiki/Law_of_cosines" target="_blank">Cosines</a> ( cos )</li>' +
                        '               <li><a href="http://en.wikipedia.org/wiki/Law_of_tangents" target="_blank">Tangents</a> ( tan )</li>' +
                        '               <li><a href="http://en.wikipedia.org/wiki/Absolute_value" target="_blank">Absolute value</a> ( abs )</li>' +
                        '           </ul>' +
                        '       </div>' +
                        '       <div class="span5">' +
                        '           <ul class="unstyled">' +
                        '               <li><a href="http://en.wikipedia.org/wiki/Truncation" target="_blank">Truncate to zero</a> ( trunc )</li>' +
                        '               <li><a href="http://en.wikipedia.org/wiki/Rounding" target="_blank">Round</a> ( round )</li>' +
                        '               <li>Sign digit ( sign )</li>' +
                        '           </ul>' +
                        '       </div>' +
                        '   </div>' +
                        '   <div class="row">' +
                        '       <h5>Constants</h5>' +
                        '       <p>Supported constants are <b>PI</b> and <b>E</b>.' +
                        '       <div class="span12">' +
                        '           <ul>' +
                        '               <li>E provides the mathematical constant E (2.718281... to available precision)</li>' +
                        '               <li>PI provides the mathematical constant π (3.141592... to available precission)</li>' +
                        '           </ul>' +
                        '       </div>' +
                        '   </div>' +
                        '</div>'
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