function ChatController() {
    return function (scope, http, httpParamSerializerJQLike, timeout, interval) {

        var start_polling = false;

        scope.show_load_previous = false;
        scope.messages = [];
        scope.message = '';
        scope.uploadFile = null;
        scope.load_message_interval = null;
        scope.audio_blob = null;

        scope.$on('startChat', function (event, arg) {
            scope.load_messages();
        });

        scope.$on('stopChat', function (event, arg) {
            interval.cancel(scope.load_message_interval);
            start_polling = false;
            scope.messages = [];
            scope.show_load_previous = false;
            scope.message = '';
            scope.uploadFile = null;
        });

        var get_user_id_queryset = function () {
            if (scope.user_id === undefined) {
                return ""
            }
            else {
                return '&user=' + scope.user_id;
            }
        };

        var handle_messages = function (response) {
            let firstId = 0;
            if (scope.messages.length > 0) {
                firstId = scope.messages[0].id;
            }

            if (response.messages.length == 0) {
                return;
            }

            let newMessages = response.messages;
            newMessages.forEach(function (message) {
                message['time_display'] = moment(message.time).calendar();
                let existMessage = scope.messages.find(element => element.id === message.id);
                if (existMessage === undefined) {
                    scope.messages.push(message);
                }
            });

            scope.messages.sort(function (a, b) {
                return a.id - b.id;
            });

            scope.show_load_previous = true;

            if (scope.messages[0].id >= firstId) {
                timeout(function () {
                    window.scrollTo(0, document.body.scrollHeight);
                    let msgHistory = $('.msg_history');
                    msgHistory.scrollTop(msgHistory.prop('scrollHeight'));
                }, 100);
            }
        };

        scope.message_key_press = function(keyEvent) {
            if (keyEvent.which == 13) {
                scope.send_message();
            }
        };

        scope.send_message = function () {
            const url = chatApi + '?send_message=1';
            var data = new FormData();
            data.append('msg', scope.message);
            if (scope.user_id !== undefined) {
                data.append('user_id', scope.user_id)
            }
            if (scope.uploadFile) {
                data.append('file', scope.uploadFile);
            }

            if (scope.audio_blob) {
                data.append('audio_file', scope.audio_blob);
            }

            scope.messages.forEach(x => {
               if (x.r) {
                   x.read = true;
               }
            });
            scope.message = '';
            scope.clear_file();
            scope.clear_record();
            http({
                url: url,
                method: 'POST',
                data: data,
                headers: {
                    'Content-Type': undefined
                }
            }).then(function (response) {
                console.log("message sent");
                handle_messages(response.data);
            }, function (error) {
                console.log(error);
            });
        };

        scope.clear_file = function () {
            scope.uploadFile = null;
        };

        scope.get_attachment_url = function(msg_id) {
            return chatApi + '?attachment_id=' + msg_id
        };

        scope.load_messages = function (previous, next) {
            if (previous == null && next == null) {
                let url = chatApi + '?receive_message=1' + get_user_id_queryset();
                http({
                    url: url,
                    method: 'GET'
                }).then(function (response) {
                    handle_messages(response.data);
                    if (start_polling == false) {
                        start_polling = true;
                        scope.load_message_interval = interval(function () {
                            if (start_polling == true) {
                                scope.load_messages(null, 1);
                            }
                        }, 3000);
                    }
                });
            } else if (previous != null) {
                let first_id = scope.messages[0].id;
                let url = chatApi + '?receive_message=1' + get_user_id_queryset() + '&prev=' + first_id;
                scope.show_load_previous = false;
                http.get(url).then(function (response) {
                    handle_messages(response.data);
                });
            } else if (next != null) {
                let url = chatApi + '?receive_message=1' + get_user_id_queryset();
                if (scope.messages.length > 0) {
                    let last_id = scope.messages[scope.messages.length - 1].id;
                    url = url + '&next=' + last_id;
                }
                http.get(url).then(function (response) {
                    handle_messages(response.data);
                });
            }
        };

        var gumStream;
        var AudioContext = window.AudioContext || window.webkitAudioContext;
        var input;
        scope.rec = null;
        scope.is_recording = false;

        scope.clear_record = function() {
            if (scope.rec) {
                scope.rec.clear()
            }
            scope.rec = null;
            scope.audio_blob = null;
        };

        scope.start_recording = function () {
            scope.is_recording = true;
            scope.audio_blob = null;
            scope.uploadFile = null;
            if (scope.rec) {
                scope.rec.clear();
            }
            var constraints = {audio: true, video: false};
            navigator.mediaDevices.getUserMedia(constraints).then(function (stream) {
                audioContext = new AudioContext();
                gumStream = stream;
                input = audioContext.createMediaStreamSource(stream);
                scope.rec = new Recorder(input,{numChannels:1});

		        //start the recording process
		        scope.rec.record();
            }).catch(function(err) {

            });
        };

        var createDownloadLink = function (blob) {
            var url = URL.createObjectURL(blob);
            scope.audio_blob = blob;
            var au = $(".type_msg .input_msg_write audio");
            au.attr('src', url);
        };

        scope.stop_recording = function () {
            scope.rec.stop();
            scope.rec.context.close();
            gumStream.getAudioTracks()[0].stop();
            scope.rec.exportWAV(createDownloadLink)
            scope.is_recording = false;
        };

    }

}

function FileModelDirective() {
    return function (parse) {
        return {
            restrict: 'A', //the directive can be used as an attribute only

            /*
             link is a function that defines functionality of directive
             scope: scope associated with the element
             element: element on which this directive used
             attrs: key value pair of element attributes
             */
            link: function (scope, element, attrs) {
                var model = parse(attrs.fileModel),
                    modelSetter = model.assign; //define a setter for demoFileModel

                //Bind change event on the element
                element.bind('change', function () {
                    //Call apply on scope, it checks for value changes and reflect them on UI
                    scope.$apply(function () {
                        //set the model value
                        modelSetter(scope, element[0].files[0]);
                    });
                });
            }
        };
    };
}