import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import JsonWebsocketConsumer
from django.utils import timezone

from chat.models import Message, ChatGroup


class ChatConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.user = self.scope['user']
        # get course id
        self.course_id = self.scope['url_route']['kwargs']['course_id']
        # make group name
        self.room_group_name = f"chat_{self.course_id}"

        # add group to db and add user to group
        chat_group, _ = ChatGroup.objects.get_or_create(group_name=self.room_group_name)
        chat_group.participants.add(self.user)
        self.chat_group = chat_group

        # add channel to group
        async_to_sync(self.channel_layer.group_add)(self.room_group_name, self.channel_name)
        print(self.room_group_name, self.channel_name)
        self.accept()

    def disconnect(self, code):

        # chat_group = ChatGroup.objects.get(group_name=self.room_group_name)
        # chat_group.participants.remove(self.user)
        self.chat_group = None

        # remove channel from group
        async_to_sync(self.channel_layer.group_discard)(self.room_group_name, self.channel_name)

    def receive(self, text_data=None, bytes_data=None, **kwargs):
        text_data_json = json.loads(text_data)
        event_type = text_data_json['type']
        message = text_data_json['message']

        now = timezone.now()

        if event_type == 'fetch_messages':
            # fetch old messages
            self.fetch_messages(text_data_json)
        else:
            msg_id = self.save_chat(message)
            # send message to group
            async_to_sync(self.channel_layer.group_send)(self.room_group_name,
                                                         {'type': 'chat_message',
                                                          'message_id': msg_id,
                                                          'creator': self.user.email,
                                                          'content': message,
                                                          'group_name': self.chat_group.id,
                                                          'created_at': now.isoformat()})

    def chat_message(self, event):
        self.send_json(content={'type': 'chat_message', 'message': [event]})

    def fetch_messages(self, data):
        messages = self.get_last_n_messages(20)
        result = []
        for message in messages:
            msg = self.message_to_json(message)
            msg['type'] = 'all_message'
            result.append(msg)

        self.send_json(content={'type': 'all_message', 'message': result})

    def save_chat(self, message):
        msg = Message.objects.create(
            creator=self.user,
            content=message,
            chat_group=self.chat_group,
        )
        return msg.id

    def get_last_n_messages(self, n=10):
        return reversed(Message.objects.filter(chat_group__group_name=self.room_group_name)[:n])

    def message_to_json(self, message):
        return {
            'message_id': message.id,
            'creator': message.creator.email,
            'content': message.content,
            'group_name': message.chat_group.id,
            'created_at': message.created_at.isoformat()
        }
