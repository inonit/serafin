var content = angular.module('content', []);

var fileTemplate = {
    url: '',
    title: ''
};

var dataTemplates = {
    'text': {
        content_type: 'text',
        content: ''
    },
    'form': {
        content_type: 'form',
        content: []
    },
    'image': {
        content_type: 'image',
        content: fileTemplate
    },
    'video': {
        content_type: 'video',
        content: fileTemplate
    },
    'audio': {
        content_type: 'audio',
        content: fileTemplate
    },
    'file': {
        content_type: 'file',
        content: fileTemplate
    },
    'numeric': {
        field_type: 'numeric',
        variable_name: '',
        label: '',
        required: false,
    },
    'string': {
        field_type: 'string',
        variable_name: '',
        label: '',
        required: false,
    },
    'textarea': {
        field_type: 'text',
        variable_name: '',
        label: '',
        required: false,
    },
    'multiplechoice': {
        field_type: 'multiplechoice',
        variable_name: '',
        label: '',
        required: false,
        alternatives: []
    },
    'multipleselection': {
        field_type: 'multipleselection',
        variable_name: '',
        label: '',
        required: false,
        alternatives: []
    },
    'alternative': {},
};

content.run(['$rootScope', function(scope) {
    if (typeof initData === 'undefined') {
        scope.data = [];
    } else {
        scope.data = initData;
    }
}]);

content.controller('contentList', ['$scope', function(scope) {
    scope.add = function(list, type) {
        list.push(dataTemplates[type]);
    };

    scope.up = function(list, index) {
        list.splice(index--, 0, list.splice(index, 1)[0]);
    };

    scope.down = function(list, index) {
        list.splice(index++, 0, list.splice(index, 1)[0]);
    };

    scope.delete = function(list, index) {
        list.splice(index, 1);
    };
}]);

content.controller('markdown', ['$scope', '$window', '$sce', function(scope, window, sce) {
    scope.md2html = function() {
        scope.html = window.marked(scope.pagelet.content);
        scope.htmlSafe = sce.trustAsHtml(scope.html);
    };
    scope.md2html();
}]);

content.directive('textarea', function() {
    // autoresize textarea as you type.
    return {
        restrict: 'E',
        link: function(scope, element, attrs) {
            var threshold    = 40,
                minHeight    = element[0].offsetHeight,
                paddingLeft  = element.css('paddingLeft'),
                paddingRight = element.css('paddingRight');

            var shadow = angular.element('<div></div>').css({
                position:   'absolute',
                top:        -10000,
                left:       -10000,
                width:      element[0].offsetWidth - parseInt(paddingLeft || 0, 10) - parseInt(paddingRight || 0, 10),
                fontSize:   element.css('fontSize'),
                fontFamily: element.css('fontFamily'),
                lineHeight: element.css('lineHeight'),
                resize:     'none'
            });

            angular.element(document.body).append(shadow);

            var update = function() {
                var times = function(string, number) {
                    for (var i = 0, r = ''; i < number; i++) {
                        r += string;
                    }
                    return r;
                };

                var val = element.val().replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/&/g, '&amp;')
                    .replace(/\n$/, '<br/>&nbsp;')
                    .replace(/\n/g, '<br/>')
                    .replace(/\s{2,}/g, function(space) {
                        return times('&nbsp;', space.length - 1) + ' ';
                    });

                shadow.html(val);

                element.css('height', Math.max(shadow[0].offsetHeight + threshold , minHeight));

                angular.element(element[0].nextSibling).css('height', element.css('height'));
            };

            scope.$on('$destroy', function() {
                shadow.remove();
            });

            element.bind('keyup keydown keypress change', update);

            if (attrs.ngModel) {
               scope.$watch(attrs.ngModel, update);
            }
        }
    };
});
