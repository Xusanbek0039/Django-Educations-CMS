from django.conf import settings
from django.db import models


class ChatGroup(models.Model):
    group_name = models.CharField(max_length=100, unique=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    chat_group = models.ForeignKey(ChatGroup, related_name='messages', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_json(self):
        return {
            'message_id': self.id,
            'creator': self.creator.email,
            'content': self.content,
            'group_name': self.chat_group,
            'created_at': self.created_at.isoformat()
        }

    def __str__(self):
        return f"{self.creator}"

    class Meta:
        ordering = ('-created_at',)
