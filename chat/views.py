from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.views.generic import View

from chat.models import Message
from courses.models import Course


# Create your views here.
class CourseChatRoom(LoginRequiredMixin, View):
    template_name = 'chat/room.html'

    def get(self, request, *args, **kwargs):
        try:
            course = self.request.user.courses_joined.get(id=kwargs['course_id'])
            chat_room = f"chat_{course.id}"
            # get old messages
            messages = reversed(Message.objects.filter(chat_group__group_name=chat_room)[:20])
            old_messages = []
            for message in messages:
                old_messages.append({
                    'type': 'all_message',
                    'message_id': message.id,
                    'creator': message.creator.email,
                    'content': message.content,
                    'group_name': message.chat_group.id,
                    'created_at': message.created_at
                })
        except Course.DoesNotExist:
            return HttpResponseForbidden()

        return render(self.request, self.template_name, {'course': course, 'old_messages': old_messages})
