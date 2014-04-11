var instanceConfig = {
    Endpoint: [
        'Dot', {
            radius: 2,
        }
    ],
    HoverPaintStyle: {
        strokeStyle: '#1e8151',
        lineWidth: 2,
    },
    ConnectionOverlays: [
        [
            'Arrow', {
                location: 1,
                id: 'arrow',
                width: 10,
            }
        ],
        [
            'Label', {
                label: 'next',
                id: 'label',
                cssClass: 'aLabel',
            }
        ]
    ],
    Container: 'plumbing'
};

var sourceConfig = {
    filter: '.ep',
    anchor: 'Continuous',
    connector: [
        'StateMachine',
    ],
    connectorStyle: {
        strokeStyle: '#5c96bc',
        lineWidth: 2,
    },
    maxConnections: 9,
    onMaxConnections: function(info, e) {
        alert('Maximum connections (' + info.maxConnections + ') reached');
    }
};

var targetConfig = {
    dropOptions: {
        hoverClass: 'dragHover'
    },
    anchor: 'Continuous'
};

var plumbing = angular.module('plumbing', []);

plumbing.service('jsPlumb', ['$rootScope', function(scope) {
    jsPlumb.ready(function() {
        scope.jsPlumb = jsPlumb.getInstance(instanceConfig);
    });
}]);

plumbing.run(['$rootScope', '$timeout', 'jsPlumb', function(scope, timeout, jsPlumbService) {

    if (typeof initData === 'undefined') {
        scope.data = {
            nodes: [],
            edges: [],
        };
    } else {
        scope.data = initData;
    }

    scope.currentNoderef = '';

    jsPlumb.ready(function() {
        scope.jsPlumb.bind('dblclick', function(c) {
            scope.jsPlumb.detach(c);
        });

        scope.jsPlumb.bind('connection', function(c) {
            c.connection.getOverlays()[1].label = c.connection.getParameters()['label'];
            scope.data.edges.push({
                label: 'next',
                source: +c.sourceId.substr(5),
                target: +c.targetId.substr(5),
            });
        });

        scope.jsPlumb.bind('connectionDetached', function(c) {
            var index;
            scope.data.edges.forEach(function(edge) {
                if (edge.source == +c.sourceId.substr(5) &&
                    edge.target == +c.targetId.substr(5)) {
                    index = scope.data.edges.indexOf(edge);
                }
            });
            scope.data.edges.splice(index, 1);
        });

        scope.jsPlumb.doWhileSuspended(function() {
            if (scope.data.edges) {
                scope.data.edges.forEach(function(edge) {
                    scope.jsPlumb.connect({
                        source: 'node_' + edge['source'],
                        target: 'node_' + edge['target'],
                        parameters: {
                            label: edge['label'],
                        }
                    });
                });
            }
        });
    });
}]);

plumbing.controller('graph', ['$scope', '$http', function(scope, http) {

    scope.addNode = function() {
        var id = scope.data.nodes.length + 1;

        scope.data.nodes.push({
            'id': id,
            'url': newNodeUrl,
            'title': '?',
            'metrics': {
                'left': '25px',
                'top': '25px'
            }
        });

        scope.currentNoderef = 'noderef_' + id;

        var win = window.open(
            addNodeUrl + '?t=id&_popup=1',
            scope.currentNoderef,
            'height=800,width=1024,resizable=yes,scrollbars=yes'
        );

        win.focus();
    };
}]);

plumbing.directive('node', ['jsPlumb', function(jsPlumbService) {
    return {
        restrict: 'C',
        controller: 'graph',
        scope: '@',
        link: function(scope, element, attrs) {
            element[0].id = 'node_' + scope.node.id;

            jsPlumb.ready(function() {
                scope.jsPlumb.draggable(element);
                scope.jsPlumb.doWhileSuspended(function() {
                    scope.jsPlumb.makeSource(element, sourceConfig);
                    scope.jsPlumb.makeTarget(element, targetConfig);
                });
            });

            element.bind('mouseup', function(e) {
                scope.$apply(function() {
                    scope.node.metrics.left = element[0].style.left;
                    scope.node.metrics.top = element[0].style.top;
                });
            });

            element.bind('dblclick', function() {
                var win = window.open(
                    scope.node.url + '?_popup=1',
                    'noderef-' + scope.node.id,
                    'height=800,width=1024,resizable=yes,scrollbars=yes'
                );
                win.focus();
            });
        }
    };
}]);

plumbing.directive('noderef', ['$http', function(http) {
    return {
        restrict: 'C',
        link: function(scope, element, attrs) {
            element[0].id = 'noderef_' + scope.node.id;

            angular.element(window).bind('focus', function(val) {
                var value = element.attr('value');
                if (value !== scope.node.id) {
                    scope.$apply(function() {
                        scope.node.id = value;
                    });
                    http.get(pageApiUrl + value).success(function(data) {
                        scope.node.title = data['title'];
                        scope.node.url = data['url'];
                    });
                }
            });
        }
    };
}]);
