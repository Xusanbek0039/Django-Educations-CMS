from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.core.cache import cache

from courses.models import Course
from students.forms import CourseEnrollForm
import logging

logger = logging.getLogger(__name__)


# Create your views here.
class StudentRegistrationView(CreateView):
    template_name = 'students/student/registration.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('students:student_course_list')

    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data

        user = authenticate(username=cd['username'], password=cd['password1'])
        login(self.request, user)
        return result


class StudentEnrollCourseView(LoginRequiredMixin, FormView):
    course = None
    form_class = CourseEnrollForm

    def form_valid(self, form):
        self.course = form.cleaned_data['course']
        self.course.students.add(self.request.user)
        logger.info(f"Student {self.request.user.email} enrolled in {self.course}")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('students:student_course_detail', args=[self.course.id])
        # return reverse_lazy('course_list')


class StudentCourseListView(LoginRequiredMixin, ListView):
    model = Course
    template_name = 'students/course/list.html'
    context_object_name = 'courses'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])


class StudentCourseDetailView(LoginRequiredMixin, DetailView):
    model = Course
    template_name = 'students/course/detail.html'
    context_object_name = 'course'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(students__in=[self.request.user])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        course = self.get_object()

        if 'module_id' in self.kwargs:
            key = f"enrolled_module_{course.id}_{self.kwargs['module_id']}"
            module = cache.get(key)
            if not module:
                module = course.modules.get(id=self.kwargs['module_id'])
                cache.set(key, module)
                logger.debug(f"Added course module {key} to cache")
            context['module'] = module
        else:
            context['module'] = course.modules.all()[0]

        return context
