/**
 * Angular directive for writing and evaluating
 * string expressions.
 * */

"use strict";


angular.module("stringExpression", [])

    .config(function($httpProvider) {
        $httpProvider.defaults.headers.common["X-Requested-With"] = "XMLHttpRequest";
    })

    .directive("stringExpression", function() {
        return {
            restrict: "E",
            replace: true,
            transclude: true,
            require: "?ngModel",
            scope: {},
            templateUrl: "template/string-expression.html",
            controller: ["$scope", function($scope) {

            }]
        }
    });