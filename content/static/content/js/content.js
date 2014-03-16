var content = angular.module('content', []);

var fileTemplate = {
    url: '',
    file_id: '',
    title: ''
};

var dataTemplates = {
    'text': {
        content_type: 'text',
        content: {
            text: '',
            html: '',
        }
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
        var marked = window.marked(scope.pagelet.content.text);
        scope.pagelet.content.html = sce.trustAsHtml(marked);
    };
    scope.md2html();
}]);

content.directive('textarea', function() {
    // autoresize textarea as you type.
    return {
        restrict: 'E',
        link: function(scope, elem, attrs) {
            var threshold    = 40,
                minHeight    = elem[0].offsetHeight,
                paddingLeft  = elem.css('paddingLeft'),
                paddingRight = elem.css('paddingRight');

            var shadow = angular.element('<div></div>').css({
                position:   'absolute',
                top:        -10000,
                left:       -10000,
                width:      elem[0].offsetWidth - parseInt(paddingLeft || 0, 10) - parseInt(paddingRight || 0, 10),
                fontSize:   elem.css('fontSize'),
                fontFamily: elem.css('fontFamily'),
                lineHeight: elem.css('lineHeight'),
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

                var val = elem.val().replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/&/g, '&amp;')
                    .replace(/\n$/, '<br/>&nbsp;')
                    .replace(/\n/g, '<br/>')
                    .replace(/\s{2,}/g, function(space) {
                        return times('&nbsp;', space.length - 1) + ' ';
                    });

                shadow.html(val);

                elem.css('height', Math.max(shadow[0].offsetHeight + threshold , minHeight));

                angular.element(elem[0].nextSibling).css('height', elem.css('height'));
            };

            scope.$on('$destroy', function() {
                shadow.remove();
            });

            elem.bind('keyup keydown keypress change', update);

            if (attrs.ngModel) {
               scope.$watch(attrs.ngModel, update);
            }
        }
    };
});

content.directive('filer', ['$compile', function(compile) {
    return {
        restrict: 'C',
        replace: true,
        link: function(scope, elem, attrs) {
            angular.element('#id_file_clear').addClass('clear').on('click', function() {
                //django.jQuery("#id_file").removeAttr("value");
                //django.jQuery("#id_file_thumbnail_img").attr("src", "{{ filer_static_prefix }}icons/nofile_48x48.png");
                //django.jQuery("#id_file_description_txt").html("");
                //django.jQuery("#id_file_clear").hide();
            });

            for (var i = 0; i < elem.children().length; i++) {
                var child = elem.children()[i];

                if (child.id == 'id_file') {
                    var file_id = angular.element(child).attr('ng-model', 'pagelet.content.file_id');
                    compile(file_id)(scope);
                }

                if (child.id) {
                    child.id = child.id.replace('id_file', 'id_file_' + scope.$parent.$index);
                }
            }
        }
    };
}]);
