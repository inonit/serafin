var content = angular.module('content', ['autocompleteSearch', 'stringExpression', 'ui.codemirror']);

var fileTemplate = {
    url: '',
    file_id: '',
    title: ''
};

var dataTemplates = {
    'text': {
        content_type: 'text',
        content: ''
    },
    'toggle': {
        content_type: 'toggle',
        content: '',
        toggle: ''
        //img_content: fileTemplate
    },
    'toggleset': {
        content_type: 'toggleset',
        content: {
            variable_name: '',
            label: '',
            value: '',
            alternatives: []
        }
    },
    'togglesetmulti': {
        content_type: 'togglesetmulti',
        content: {
            variable_name: '',
            label: '',
            value: [],
            alternatives: []
        }
    },
    'conditionalset': {
        content_type: 'conditionalset',
        content: []
    },
    'conditionaltext': {
        expression: '',
        content: ''
    },
    'condition': {
        var_name: '',
        logical_operator: '',
        operator: '',
        value: ''
    },
    'expression': {
        content_type: 'expression',
        content: {
            variable_name: '',
            value: ''
        }
    },
    'form': {
        content_type: 'form',
        content: []
    },
    'quiz': {
        content_type: 'quiz',
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
    'toggleitem': {
        label: '',
        value: '',
        text: ''
    },
    'numeric': {
        field_type: 'numeric',
        variable_name: '',
        label: '',
        required: false
    },
    'string': {
        field_type: 'string',
        variable_name: '',
        label: '',
        required: false
    },
    'textarea': {
        field_type: 'text',
        variable_name: '',
        label: '',
        required: false
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
        value: [],
        alternatives: []
    },
    'email': {
        field_type: 'email',
        variable_name: ''
    },
    'password': {
        field_type: 'password',
        variable_name: ''
    },
    'hiddenfield': {
        field_type: 'hiddenfield',
        variable_name: ''
    },
    'question': {
        question: '',
        variable_name: '',
        right: '',
        wrong: '',
        alternatives: []
    },
    'alternative': {
        label: '',
        value: ''
    }
};

content.run(['$rootScope', '$http', function (scope, http) {
    if (!initData) {
        scope.data = [];
    } else {
        scope.data = initData;
    }

    scope.variables = [];
    http.get('/api/system/variables/').then(function (response) {
        if (typeof reservedVars !== 'undefined') {
            scope.variables = response.data.concat(reservedVars || []);
        } else {
            scope.variables = response.data;
        }

    });

    scope.editorOpts = {
        mode: 'python',
        theme: 'lucario',
        lineNumbers: true,
        lineWrapping: true
    };

    scope.codemirrorLoaded = function (_editor) {
        // for futur improvement

        // Editor part
        /*var _doc = _editor.getDoc();
        _editor.focus();
  
        // Options
        _editor.setOption('firstLineNumber', 10);
        _doc.markClean()
  
        // Events
        _editor.on("beforeChange", function(){ ... });
        _editor.on("change", function(){ ... });*/
        return true
    };

}]);

content.controller('contentArray', ['$scope', function (scope) {
    scope.add = function (array, type) {
        array.push(angular.copy(dataTemplates[type]));
    };

    scope.up = function (array, index) {
        array.splice(index--, 0, array.splice(index, 1)[0]);
    };

    scope.down = function (array, index) {
        array.splice(index++, 0, array.splice(index, 1)[0]);
    };

    scope.delete = function (array, index) {
        array.splice(index, 1);
    };

}]);

content.controller('markdown', ['$scope', '$window', '$sce', function (scope, window, sce) {
    scope.html = '';
    scope.md2html = function (content) {
        var marked = window.marked(content);
        marked = marked.replace(/({{.*?}})/g, '<span class="markup">$&</span>');
        marked = marked.replace(/([[.*?]])/g, '<span class="markup">$&</span>');
        marked = marked.replace(/(login_link)/g, '<span class="markup">$&</span>');
        marked = marked.replace(/(reply:\d+)/g, '<span class="markup">$&</span>');
        scope.html = sce.trustAsHtml(marked);
    };
}]);

content.directive('markdownText', ['$timeout', function (timeout) {
    return {
        restrict: 'C',
        require: 'ngModel',
        controller: 'markdown',
        link: function (scope, elem, attrs, ngModel) {
            timeout(function () {
                scope.md2html(ngModel.$modelValue);
            });
            ngModel.$viewChangeListeners.push(function () {
                scope.md2html(ngModel.$modelValue);
            });
        }
    };
}]);

content.directive('textarea', function () {
    // autoresize textarea as you type.
    return {
        restrict: 'E',
        link: function (scope, elem, attrs) {
            var threshold = 40,
                minHeight = elem[0].offsetHeight,
                paddingLeft = elem.css('paddingLeft'),
                paddingRight = elem.css('paddingRight');

            var shadow = angular.element('<div></div>').css({
                position: 'absolute',
                top: -10000,
                left: -10000,
                width: elem[0].offsetWidth - parseInt(paddingLeft || 0, 10) - parseInt(paddingRight || 0, 10),
                fontSize: elem.css('fontSize'),
                fontFamily: elem.css('fontFamily'),
                lineHeight: elem.css('lineHeight'),
                resize: 'none'
            });

            angular.element(document.body).append(shadow);

            var update = function () {
                var times = function (string, number) {
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
                    .replace(/\s{2,}/g, function (space) {
                        return times('&nbsp;', space.length - 1) ' ';
                    });

                shadow.html(val);
                elem.css('height', Math.max(shadow[0].offsetHeight threshold, minHeight));
                angular.element(elem[0].nextSibling).css('height', elem.css('height'));
            };

            scope.$on('$destroy', function () {
                shadow.remove();
            });

            elem.bind('keyup keydown keypress change', update);

            if (attrs.ngModel) {
                scope.$watch(attrs.ngModel, update);
            }
        }
    };
});

content.directive('filer', ['$compile', '$http', function (compile, http) {
    return {
        restrict: 'C',
        replace: true,
        link: function (scope, elem, attrs) {
            scope.noimg = elem.find('#id_file_thumbnail_img').attr('src');
            var index = scope.$parent.$index;
            var url = filerApi + scope.pagelet.content_type + '/';

            if (scope.pagelet.content_type == 'toggle') {
                if (scope.pagelet.img_content == undefined)
                    scope.pagelet.img_content = angular.copy(fileTemplate);
                scope.contentProxy = scope.pagelet.img_content
            } else {
                scope.contentProxy = scope.pagelet.content
            }
        if(scope.pagelet.content_type == 'toggle') {
    if (scope.pagelet.img_content == undefined)
        scope.pagelet.img_content = angular.copy(fileTemplate);
    scope.contentProxy = scope.pagelet.img_content
} else {
    scope.contentProxy = scope.pagelet.content
}

// clear on click
elem.find('.filerClearer').on('click', function () {
    scope.$apply(function () {
        scope.contentProxy.file_id = '';
        scope.contentProxy.url = '';
        scope.contentProxy.thumbnail = '';
        scope.contentProxy.description = '';
    })
});

// set up popup handler
elem.find('#id_file_lookup')
    .attr('onclick', 'return showRelatedObjectLookupPopup(this)');

// differentiate externally interacting elements
elem.find('#id_file')[0].id = 'id_file_' index;
elem.find('#id_file_lookup')[0].id = 'id_file_lookup_' index;

// set models
var file_id = elem.find('#id_file' index)
    .attr('ng-model', 'pagelet.content.file_id');
var thumb = elem.find('.thumbnail_img')
    .attr('ng-src', scope.contentProxy.thumbnail);
var name = elem.find('.description_text')
    .attr('ng-bind', 'pagelet.content.description');
compile(file_id)(scope);
compile(thumb)(scope);
compile(name)(scope);

// receive on select
angular.element(window).bind('focus', function (val) {
    var value = elem.find('#id_file_' index).attr('value');
    if (value && value !== scope.contentProxy.file_id) {
        scope.$apply(function () {
            scope.contentProxy.file_id = value;
        });
        http.get(url value '/').success(function (data) {
            scope.contentProxy.url = data['url'];
            scope.contentProxy.thumbnail = data['thumbnail'];
            scope.contentProxy.description = data['description'];
        });
    }
});

// populate on load
if (scope.contentProxy.file_id) {
    http.get(url scope.contentProxy.file_id '/').success(function (data) {
        elem.find('.thumbnail_img').removeClass('hidden');
        elem.find('.description_text').removeClass('hidden');
        elem.find('.filerClearer').removeClass('hidden');
        elem.find('#id_file_lookup_' index).addClass('hidden');
    });
}

// watch and update actual content
scope.$watchCollection('contentProxy', function (content) {
    if (scope.pagelet.content_type == 'toggle')
        scope.pagelet.img_content = content
    else
        scope.pagelet.content = content;
})
        }
    };
}]);

content.directive('optTitle', [function () {
    return {
        restrict: 'A',
        link: function (scope, element, attrs) {
            element.bind('mouseenter', function () {
                element[0].title = element.children(':selected')[0].title
            })
        }
    };
}]);
