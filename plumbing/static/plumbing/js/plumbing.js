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
        strokeStyle: '#4DAF7C',
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
        strokeStyle: '#5C97BF',
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


var plumbing = angular.module('plumbing', []);

plumbing.service('jsPlumb', ['$rootScope', function(scope) {

    jsPlumb.ready(function() {

        // create instance
        scope.jsPlumb = jsPlumb.getInstance(instanceConfig);

        // intercept connection
        scope.jsPlumb.bind('beforeDrop', function(c) {
            scope.$apply(function() {
                scope.data.edges.push({
                    id: scope.data.edges.length + 1,
                    type: '',
                    source: +c.sourceId.substr(5),
                    target: +c.targetId.substr(5),
                    conditions: [],
                });
            });
        });
    });
}]);

plumbing.run(['$rootScope', function(scope) {

    if (typeof initData === 'undefined') {
        scope.data = {
            nodes: [{
                id: 0,
                type: 'start',
                title: 'Start',
                metrics: {
                    left: '25px',
                    top: '75px'
                }
            }],
            edges: [],
        };
    } else {
        scope.data = initData;
    }
    scope.currentNoderef = '';
    scope.variables = initVars;
    scope.showConditions = -1;
    scope.showDelay = -1;

}]);

plumbing.controller('graph', ['$scope', 'jsPlumb', function(scope, jsPlumbService) {

        scope.addNode = function(type) {
            var id = scope.data.nodes.length;

            if (type == 'delay') {
                scope.data.nodes.push({
                    id: id,
                    type: 'delay',
                    delay: {
                        number: 0,
                        unit: '',
                    },
                    metrics: {
                        left: '300px',
                        top: '100px'
                    }
                });
                return;
            }

            var newNodeUrl = newPageUrl;
            var addNodeUrl = addPageUrl;
            if (type == 'email') {
                newNodeUrl = newEmailUrl;
                addNodeUrl = addEmailUrl;
            } else if (type == 'sms') {
                newNodeUrl = newSMSUrl;
                addNodeUrl = addSMSUrl;
            }

            scope.data.nodes.push({
                id: id,
                type: type,
                ref_id: '',
                ref_url: newNodeUrl,
                title: '?',
                metrics: {
                    left: '300px',
                    top: '100px'
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

        scope.close = function() {
            scope.showDelay = -1;
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

                // ensure connection is detached on edge destruction
                scope.$on('$destroy', function() {
                    scope.settings.remove();
                    scope.$parent.showDelay = -1;
                    scope.data.edges.forEach(function(edge) {
                        if (edge.source == scope.node.id ||
                            edge.target == scope.node.id) {
                            var index = scope.data.edges.indexOf(edge);
                            scope.data.edges.splice(index, 1);
                        }
                    });
                });
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
                    scope.node.metrics.left = element[0].style.left;
                    scope.node.metrics.top = element[0].style.top;
                });
            });

            // open a django popup or delay conditions on double click
            element.bind('dblclick', function() {
                if (scope.node.id > 0) {
                    if (scope.node.type == 'delay') {
                        scope.$apply(function() {
                            scope.$parent.showDelay = scope.$index;
                            scope.$parent.showConditions = -1;
                        });
                    } else {
                        window.open(
                            scope.node.ref_url + '?_popup=1',
                            'noderef_' + scope.node.id,
                            'height=800,width=1024,resizable=yes,scrollbars=yes'
                        ).focus();
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
        controller: ['$scope', function(scope) {

            scope.deleteEdge = function(index) {
                scope.data.edges.splice(index, 1);
            };

            scope.addCondition = function() {
                scope.edge.conditions.push({
                    var_name: '',
                    operator: '',
                    value: '',
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

            jsPlumb.ready(function() {

                var source_type = scope.data.nodes[scope.edge.source].type;
                var target_type = scope.data.nodes[scope.edge.target].type;

                // if edge is from special node to page, delete and return
                if ((source_type == 'email' ||
                     source_type == 'sms' ||
                     source_type == 'delay') &&
                    target_type == 'page') {
                    scope.deleteEdge(scope.$index);
                    return;
                }

                // set edge type
                scope.edge.type = 'normal';

                if (target_type != 'page') {
                    scope.edge.type = 'special';
                }

                // finally make connection and add overlay
                scope.connection = scope.jsPlumb.connect({
                    source: 'node_' + scope.edge.source,
                    target: 'node_' + scope.edge.target,
                    overlays: [[
                        'Custom', {
                            cssClass: 'overlay box',
                            create: function(component) {
                                return element.find('.overlay');
                            }
                        }
                    ]]
                });
            });

            // ensure connection is detached on edge destruction
            scope.$on('$destroy', function() {
                scope.jsPlumb.detach(scope.connection);
                scope.$parent.showConditions = -1;
            });

            // show full interface on double click
            element.find('.overlay').bind('dblclick', function() {
                scope.$apply(function() {
                    scope.$parent.showConditions = scope.$index;
                    scope.$parent.showDelay = -1;
                });
            });
        }
    };
}]);
