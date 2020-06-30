function ChatController() {
    return function (scope, http, httpParamSerializerJQLike, timeout, interval) {

        var start_polling = false;

        scope.show_load_previous = false;
        scope.messages = [];
        scope.load_message_interval = null;

        scope.$on('startChat', function (event, arg) {
            scope.load_messages();
        });

        scope.$on('stopChat', function (event, arg) {
            interval.cancel(scope.load_message_interval);
            start_polling = false;
            scope.messages = [];
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

            if (newMessages.length > 0) {
                scope.show_load_previous = true;
            }

            if (newMessages.length > 0 && scope.messages[0].id >= firstId) {
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
            var data;
            if (scope.user_id === undefined) {
                data = httpParamSerializerJQLike({'msg': scope.message});
            }
            else {
                data = httpParamSerializerJQLike({'msg': scope.message, 'user_id': scope.user_id})
            }
            scope.messages.forEach(x => {
               if (x.r) {
                   x.read = true;
               }
            });
            scope.message = '';
            http({
                url: url,
                method: 'POST',
                data: data,
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            }).then(function (response) {
                console.log("message sent");
                handle_messages(response.data);
            });
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
                let last_id = scope.messages[scope.messages.length - 1].id;
                let url = chatApi + '?receive_message=1' + get_user_id_queryset() + '&next=' + last_id;
                http.get(url).then(function (response) {
                    handle_messages(response.data);
                });

            }
        };
    }

}