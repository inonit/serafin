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

        // timeout to avoid race condition
        timeout(function() {
            scope.jsPlumb.doWhileSuspended(function() {
                scope.data.edges.forEach(function(edge) {
                    scope.jsPlumb.connect({
                        source: 'node_' + edge['source'],
                        target: 'node_' + edge['target'],
                        parameters: {
                            label: edge['label'],
                        }
                    });
                });
            });

            scope.jsPlumb.bind('dblclick', function(c) {
                scope.jsPlumb.detach(c);
            });

            // set overlay and push to scope on connection
            scope.jsPlumb.bind('connection', function(c) {
                c.connection.getOverlays()[1].label = c.connection.getParameters()['label'];
                scope.$apply(function() {
                    scope.data.edges.push({
                        label: 'next',
                        source: +c.sourceId.substr(5),
                        target: +c.targetId.substr(5),
                    });
                });
            });

            // remove edge on detach
            scope.jsPlumb.bind('connectionDetached', function(c) {
                scope.data.edges.forEach(function(edge) {
                    if (edge.source == +c.sourceId.substr(5) &&
                        edge.target == +c.targetId.substr(5)) {
                        scope.$apply(function() {
                            scope.data.edges.splice(
                                scope.data.edges.indexOf(edge), 1
                            );
                        });
                    }
                });
            });

        });
    });
}]);

plumbing.controller('graph', ['$scope', 'jsPlumb', function(scope, jsPlumbService) {

    scope.addNode = function() {
        var id = scope.data.nodes.length + 1;

        scope.data.nodes.push({
            'id': id,
            'ref_id': '',
            'url': newNodeUrl,
            'title': '?',
            'metrics': {
                'left': '25px',
                'top': '25px'
            }
        });

        // immediately opens a django popup to select the source for the node
        scope.currentNoderef = 'noderef_' + id;
        window.open(
            addNodeUrl + '?t=id&_popup=1',
            scope.currentNoderef,
            'height=800,width=1024,resizable=yes,scrollbars=yes'
        ).focus();
    };

    scope.deleteNode = function(index) {
        var node = scope.data.nodes[index];
        scope.jsPlumb.detachAllConnections('node_' + node.id);
        scope.data.nodes.splice(index, 1);
    };

}]);

plumbing.directive('node', ['jsPlumb', function(jsPlumbService) {
    return {
        restrict: 'C',
        controller: 'graph',
        scope: '@',
        link: function(scope, element, attrs) {
            // set id here to avoid race condition
            element[0].id = 'node_' + scope.node.id;

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
                    scope.node.metrics.left = element[0].style.left;
                    scope.node.metrics.top = element[0].style.top;
                });
            });

            // opens a django popup on double click
            element.bind('dblclick', function() {
                window.open(
                    scope.node.url + '?_popup=1',
                    'noderef_' + scope.node.id,
                    'height=800,width=1024,resizable=yes,scrollbars=yes'
                ).focus();
            });
        }
    };
}]);

plumbing.directive('noderef', ['$http', function(http) {
    return {
        restrict: 'C',
        link: function(scope, element, attrs) {
            // set id here to avoid race condition
            element[0].id = 'noderef_' + scope.node.id;

            // focus will return to the window when a popup closes
            // if the value of a noderef has changed, it will not be picked up automatically
            // add it to the scope if it has changed
            angular.element(window).bind('focus', function(val) {
                var value = element.attr('value');
                if (value !== scope.node.ref_id) {
                    scope.$apply(function() {
                        scope.node.ref_id = value;
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
