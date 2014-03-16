var urlOnClick = '/admin/system/page/add/';

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

    console.log((typeof initData === 'undefined'))
    if (typeof initData === 'undefined') {
        scope.data = {
            nodes: [],
            edges: [],
        };
    } else {
        scope.data = initData;
    }

    //timeout(function() {
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
                if (scope.data.edges)
                scope.data.edges.forEach(function(edge) {
                    scope.jsPlumb.connect({
                        source: 'node-' + edge['source'],
                        target: 'node-' + edge['target'],
                        parameters: {
                            label: edge['label'],
                        }
                    });
                });
            });
        });
    //});
}]);

plumbing.controller('graph', ['$scope', function(scope) {
    scope.newNode = function() {
        scope.data.nodes.push({
            'id': '',
            'url': urlOnClick,
            'title': '?',
            'metrics': {
                'left': '100px',
                'top': '100px'
            }
        });
    };
    scope.addNode = function() {
        scope.data.nodes.push({
            'id': scope.data.nodes.length + 1,
            'url': urlOnClick,
            'title': '?',
            'metrics': {
                'left': '100px',
                'top': '100px'
            }
        });
    };
}]);

plumbing.directive('node', ['jsPlumb', function(jsPlumbService) {
    return {
        restrict: 'C',
        controller: 'graph',
        scope: '@',
        link: function(scope, element, attrs) {
            // set id here to avoid jQuery conflict
            element[0].id = 'node-' + scope.node.id;

            jsPlumb.ready(function() {
                scope.jsPlumb.draggable(element);
                scope.jsPlumb.doWhileSuspended(function() {
                    scope.jsPlumb.makeSource(element, sourceConfig);
                    scope.jsPlumb.makeTarget(element, targetConfig);
                });
            });

            element.bind('dblclick', function() {
                var win = window.open(scope.node.url + '?_popup=1', 'nodeRef', 'height=800,width=1024,resizable=yes,scrollbars=yes');
                win.focus();
                angular.element(win).find('name=[_save]').bind('click', function() {
                    console.log('object saved');
                });
            });
        }
    };
}]);

plumbing.directive('nodeRef', function() {
    return {
        restrict: 'C',
        link: function(scope, element, attrs) {
            // MutationObserver would be nice, but has low support
            var lastEvent;
            var lastValue = element[0].value;
            angular.element(window).bind('focus', function(val) {
                if (lastEvent !== 'focus' &&
                    lastValue !== element[0].value) {
                    lastEvent = focus;
                    lastValue = element[0].value;
                    console.log('value changed');
                }
            });
        }
    };
});
