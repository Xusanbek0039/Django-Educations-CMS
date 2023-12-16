$(document).ready(function () {
    const url = 'ws://' + window.location.host + '/ws/chat/room/' + '{{ course.id }}/';
    const chatSocket = new ReconnectingWebSocket(url);

    chatSocket.onopen = function (e) {
        console.log('connection ready')
        // chatSocket.send(
        //     JSON.stringify({'type': 'fetch_messages', 'message': 'hello'})
        // )
    };

    chatSocket.onmessage = function (e) {
        const data = JSON.parse(e.data);
        const msgType = data.type;
        const messageObj = data.message

        const $chat = $('#chat');

        for (const i in messageObj) {
            const msg = messageObj[i];
            const message = msg.content;
            const user = msg.creator;
            const dateOptions = {hour: 'numeric', minute: 'numeric', hour12: true};
            const datetime = new Date(msg['created_at']).toLocaleString('en', dateOptions);
            const isMe = user === '{{request.user}}';

            const name = isMe ? 'Me' : user;


            const msgSourceBG = isMe ? 'chat-bg-me' : 'chat-bg-other';
            const msgAlignSource = isMe ? 'justify-content-end' : '';

            $chat.append(
                '<div class="w-100 d-inline-flex mb-2 ' + msgAlignSource + '">' +
                '<div class="w-75 p-2 text-break ' + msgSourceBG + '"><small class="fw-bold">' + name + '<span class="fw-lighter fst-italic"> ' + datetime + '</span></small><br>' + message + '</div>' +
                '</div>'
            );
        }


        $chat.scrollTop($chat[0].scrollHeight);

    };

    chatSocket.onclose = function (e) {
        console.log('Chat socket closed unexpectedly')
    };

    chatSocket.onerror = function (e) {
        console.log(e)
    };

    const $input = $('#chat-message-input');
    const $submit = $('#chat-message-submit');

    $submit.click(function () {
        const message = $input.val();
        if (message) {
            chatSocket.send(JSON.stringify({'type': 'single_message', 'message': message}));
            $input.val('');
            $input.focus();
        }
    });

    $input.focus();
    $input.keyup(function (e) {
        if (e.keyCode === 13) {
            $submit.click()
        }
    });
});