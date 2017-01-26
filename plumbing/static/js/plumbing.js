var undefined_p = function(value) {
    return typeof value === 'undefined';
}

var instanceConfig = {
    Container: 'plumbing',
    Endpoint: [
        'Dot', {
            radius: 3,
        }
    ],
    ConnectionOverlays: [
        [
            'Arrow', {
                location: 1,
                id: 'arrow',
                width: 10,
            }
        ],
    ],
    HoverPaintStyle: {
        lineWidth: 2,
    }
};

var sourceConfig = {
    filter: '.ep',
    anchor: 'Continuous',
    connector: [
        'StateMachine',
    ],
    connectorStyle: {
        lineWidth: 2,
    },
    maxConnections: 9,
    onMaxConnections: function(info, e) {
        alert('Maximum connections of ' + info.maxConnections + ' reached');
    }
};

var targetConfig = {
    dropOptions: {
        hoverClass: 'dragHover'
    },
    anchor: 'Continuous'
};


var plumbing = angular.module('plumbing', ['autocompleteSearch', 'stringExpression']);

plumbing.service('jsPlumb', ['$rootScope', function(scope) {

    jsPlumb.ready(function() {

        // create instance
        scope.jsPlumb = jsPlumb.getInstance(instanceConfig);

        // intercept connection
        scope.jsPlumb.bind('beforeDrop', function(c) {
            var id = 1;
            if (scope.data.edges.length) {
                id = scope.data.edges[scope.data.edges.length-1].id + 1;
            }
            scope.$apply(function() {
                scope.data.edges.push({
                    id: id,
                    type: '',
                    source: +c.sourceId.substr(5),
                    target: +c.targetId.substr(5),
                    expression: '',
                });
            });
        });
    });
}]);

plumbing.run(['$rootScope', '$http', function(scope, http) {

    scope.data = initData;
    if (scope.data.nodes && scope.data.nodes.length === 0)
        scope.data.nodes = [{
            id: 0,
            type: 'start',
            title: 'Start',
            metrics: {
                left: '25px',
                top: '75px'
            }
        }];

    scope.showConditions = -1;
    scope.showSettings = -1;

    scope.variables = [];
    http.get('/api/system/variables/').success(function (data) {
        scope.variables = data.concat(reservedVars || []);
    });

}]);

plumbing.factory('variables', ['$http', function(http) {
    var variables = null;
    return {
        get: function() {
            if (variables) return variables;

            variables = http.get('/api/system/variables/').success(function(data) {
                return data;
            });

            return variables
        }
    }
}]);

plumbing.controller('graph', ['$scope', 'jsPlumb', function(scope, jsPlumbService) {

    var SystemUrl = function(type) {
        this.type = type;

        this.get = function() {
            return adminUrl + 'system/' + this.type + '/';
        };

        this.add = function() {
            return adminUrl + 'system/' + this.type + '/add/';
        };
    };

    // scrolling
    scope.scrolling = {
        locked: false,
        x: 0,
        y: 0,
        prevX: null,
        prevY: null
    };

    scope.startScrolling = function(e) {
        var graph = document.querySelector('#plumbing');
        if (e.target === graph) {
            scope.scrolling.locked = true;
        }
    };

    scope.scroll = function(e) {
        if (scope.scrolling.locked === true) {
            var x = e.clientX;
            var y = e.clientY;
            if (scope.scrolling.prevX === null || scope.scrolling.prevY === null) {
                scope.scrolling.prevX = x;
                scope.scrolling.prevY = y;
            }
            var shiftX =
                scope.scrolling.prevX === x ? 0 :
                scope.scrolling.prevX - x;
            var shiftY =
                scope.scrolling.prevY === y ? 0 :
                scope.scrolling.prevY - y;

            scope.scrolling.x -= shiftX;
            scope.scrolling.y -= shiftY;
            scope.scrolling.prevX = x;
            scope.scrolling.prevY = y;

            scope.jsPlumb.repaintEverything();
        }
    };

    scope.stopScrolling = function() {
        scope.scrolling.prevX = null;
        scope.scrolling.prevY = null;
        scope.scrolling.locked = false;
        scope.jsPlumb.repaintEverything();
    }
    // end of scrolling

    scope.addNode = function(type) {
        var id = 1;
        if (scope.data.nodes.length) {
            id = scope.data.nodes[scope.data.nodes.length - 1].id + 1;
        }

        if (type == 'delay') {
            scope.data.nodes.push({
                id: id,
                type: type,
                delay: {
                    number: 0,
                    unit: '',
                },
                metrics: {
                    left: (300 - scope.scrolling.x) + 'px',
                    top: (100 - scope.scrolling.y) + 'px'
                }
            });
            return;
        }

        if (type == 'expression') {
            scope.data.nodes.push({
                id: id,
                type: type,
                expression: '',
                variable_name: '',
                metrics: {
                    left: (300 - scope.scrolling.x) + 'px',
                    top: (100 - scope.scrolling.y) + 'px'
                }
            });
            return;
        }

        if (type == 'register' || type == 'enroll' || type == 'leave' || type == 'wait') {
            scope.data.nodes.push({
                id: id,
                type: type,
                metrics: {
                    left: (300 - scope.scrolling.x) + 'px',
                    top: (100 - scope.scrolling.y) + 'px'
                }
            });
            return;
        }

        var url = new SystemUrl(type == 'background_session' ? 'session' : type);

        var node = {
            id: id,
            type: type,
            ref_id: '',
            ref_url: url.add(),
            title: '?',
            metrics: {
                left: (300 - scope.scrolling.x) + 'px',
                top: (100 - scope.scrolling.y) + 'px'
            }
        };

        scope.data.nodes.push(node);

        scope.popup(url.get(), id);
    };
    scope.getMetrics = function(node) {
        var x = parseInt(node.metrics.left) + scope.scrolling.x;
        var y = parseInt(node.metrics.top) + scope.scrolling.y;
        return {'left': x + 'px', 'top': y + 'px'};
    };

    scope.deleteNode = function(index) {
        var node = scope.data.nodes[index];

        var validEdges = [];
        scope.data.edges.forEach(function(edge) {
            if (edge.source != node.id &&
                edge.target != node.id) {
                validEdges.push(edge)
            }
        });

        scope.data.edges = validEdges;
        scope.data.nodes.splice(index, 1);
    };

    scope.close = function() {
        scope.showSettings = -1;
    };

    scope.popup = function(url, id) {
        window.open(
            url + '?_popup=1',
            'noderef_' + id,
            'height=800,width=1024,resizable=yes,scrollbars=yes'
        );
    };
}]);

plumbing.directive('node', ['$timeout', 'jsPlumb', function(timeout, jsPlumbService) {
    return {
        restrict: 'C',
        link: function(scope, element, attrs) {
            // set id here to avoid race condition
            element[0].id = 'node_' + scope.node.id;

            // wait for DOM update, then displace settings
            timeout(function() {
                scope.settings = element.find('.settings');
                element.parent().find('.floatbox').append(scope.settings);
            });

            // ensure connection is detached on edge destruction
            scope.$on('$destroy', function() {
                scope.settings.remove();
                scope.$parent.showSettings = -1;
            });

            // set up jsPlumb for this node
            jsPlumb.ready(function() {
                scope.jsPlumb.draggable(element);
                scope.jsPlumb.doWhileSuspended(function() {
                    scope.jsPlumb.makeSource(element, sourceConfig);
                    scope.jsPlumb.makeTarget(element, targetConfig);
                });
            });

            // apply changes in metrics when a drag move ends
            element.bind('mouseup', function(e) {
                scope.$apply(function() {
                    scope.scrolling.locked = false;
                    var x = parseInt(element[0].style.left) - scope.scrolling.x;
                    var y = parseInt(element[0].style.top) - scope.scrolling.y;
                    scope.node.metrics.left = x + 'px';
                    scope.node.metrics.top = y + 'px';
                });
            });
            element.bind('mousedown', function(e) {
                scope.$apply(function() {
                    scope.scrolling.locked = 'node';
                });
            });

            // open a django popup, conditions on double click
            element.bind('dblclick', function() {

                if (scope.node.id > 0) {
                    if (scope.node.type == 'delay' ||
                        scope.node.type == 'expression') {
                        scope.$apply(function() {
                            scope.$parent.showSettings = scope.$index;
                            scope.$parent.showConditions = -1;
                        });
                    } else if (scope.node.type == 'register' ||
                               scope.node.type == 'enroll' ||
                               scope.node.type == 'leave' ||
                               scope.node.type == 'wait') {
                        // do nothing
                    } else {
                        scope.popup(
                            scope.node.ref_url,
                            scope.node.id
                        );
                    }
                }
            });
        }
    };
}]);

plumbing.directive('noderef', ['$http', function(http) {
    return {
        restrict: 'C',
        link: function(scope, element, attrs) {
            // focus will return to the window when a popup closes
            // if the value of a noderef has changed, it will not be picked up automatically
            // add it to the scope if it has changed
            angular.element(window).bind('focus', function(val) {
                var value = element.attr('value');
                if (value !== scope.node.ref_id) {
                    scope.$apply(function() {
                        scope.node.ref_id = value;
                    });
                    http.get(nodeApiUrl + scope.node.type + '/' + value).success(function(data) {
                        scope.node.title = data['title'];
                        scope.node.ref_url = data['url'];
                    });
                }
            });
        }
    };
}]);

plumbing.directive('edge', ['jsPlumb', function(jsPlumbService) {
    return {
        restrict: 'C',
        controller: ['$scope', 'variables', function(scope, variables) {

            scope.variables = [];
            scope.logical_operators = ['AND', 'OR'];
            variables.get().then(function(promise) {
                scope.variables = promise.data.concat(reservedVars);
            });

            scope.log = function(log) {
                console.log(log)
            }

            scope.deleteEdge = function(index) {
                scope.data.edges.splice(index, 1);
            };

            scope.addCondition = function() {
                scope.edge.conditions.push({
                    var_name: '',
                    logical_operator: '',
                    operator: '',
                    value: ''
                });
            };

            scope.deleteCondition = function(index) {
                scope.edge.conditions.splice(index, 1);
            };

            scope.close = function() {
                scope.$parent.showConditions = -1;
            };
        }],
        link: function(scope, element, attrs) {

            // ensure connection is detached on edge destruction
            scope.$on('$destroy', function() {
                scope.$parent.showConditions = -1;
                scope.jsPlumb.detach(scope.connection);
            });

            // show full interface on double click
            element.find('.overlay').bind('dblclick', function() {
                scope.$apply(function() {
                    scope.$parent.showConditions = scope.$index;
                    scope.$parent.showSettings = -1;
                });
            });

            jsPlumb.ready(function() {

                var source_type, target_type;
                scope.data.nodes.forEach(function(node) {
                    if (node.id === scope.edge.source)
                        source_type = node.type;
                    if (node.id === scope.edge.target)
                        target_type = node.type;
                });

                var foreground = [
                    'start', 'page', 'session', 'wait'
                ]
                var background = [
                    'email', 'sms', 'register', 'enroll', 'leave', 'delay', 'background_session'
                ]

                // disallow/delete edge with start as target,
                // or from background node to foreground node
                if (target_type == 'start' || (
                        background.indexOf(source_type) > -1 &&
                        foreground.indexOf(target_type) > -1
                    )) {
                    scope.deleteEdge(scope.$index);
                    return;
                }

                // set edge type
                scope.edge.type = 'normal';

                if (background.indexOf(target_type) > -1 ||
                    target_type == 'expression') {
                    scope.edge.type = 'special';
                }

                // finally make connection and add overlay
                scope.connection = scope.jsPlumb.connect({
                    source: 'node_' + scope.edge.source,
                    target: 'node_' + scope.edge.target,
                    cssClass: scope.edge.type,
                    overlays: [[
                        'Custom', {
                            cssClass: 'overlay box ' + scope.edge.type,
                            create: function(component) {
                                return element.find('.overlay');
                            }
                        }
                    ]]
                });
            });
        }
    };
}]);

plumbing.directive('optTitle', [function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            element.bind('mouseenter', function() {
                element[0].title = element.children(':selected')[0].title
            })
        }
    };
}]);
