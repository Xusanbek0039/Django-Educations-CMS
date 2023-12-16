from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import routers

from courses.api import views

schema_view = get_schema_view(
    openapi.Info(
        title="Educa API",
        default_version='v1',
        description="Educa description",
    ),
    public=True,
)

router = routers.DefaultRouter()
router.register('courses', views.CourseViewSet)

app_name = 'courses_api'

urlpatterns = [
    path('subjects/', views.SubjectListView.as_view(), name='subject_list'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject_detail'),
    # path('courses/<pk>/enroll/', views.CourseEnrollView.as_view(), name='course_enroll'),
    path('', include(router.urls)),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0))
]
