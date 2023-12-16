from django.urls import path
from chat import views

app_name = 'chat'

urlpatterns = [
    path('room/<int:course_id>/', views.CourseChatRoom.as_view(), name='course_chat_room')
]