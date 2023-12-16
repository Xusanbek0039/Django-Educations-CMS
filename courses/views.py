import logging

from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.cache import cache
from django.db.models import Count
from django.forms.models import modelform_factory
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.base import TemplateResponseMixin, View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView

from courses.forms import ModuleFormset
from courses.models import Course, Module, Content, Subject
from students.forms import CourseEnrollForm


logger = logging.getLogger(__name__)


class OwnerMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin:
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    context_object_name = 'course_object'
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'


class CourseUpdateMixin(OwnerCourseEditMixin, UpdateView):
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    context_object_name = 'course_object'
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/course/formset.html'
    course = None

    def get_formset(self, data=None):
        return ModuleFormset(instance=self.course, data=data)

    def dispatch(self, request, *args, **kwargs):
        self.course = get_object_or_404(Course, id=kwargs['pk'], owner=request.user)
        return super().dispatch(request, kwargs['pk'])

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response(context={'course': self.course, 'formset': formset}, **kwargs)

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        print('invalid')
        return self.render_to_response(context={'course': self.course, 'formset': formset}, **kwargs)


class ContentCreateUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/content/form.html'
    module = None
    model = None
    content_obj = None

    def get_model(self, model_name):
        if model_name in ['text', 'file', 'image', 'video']:
            return apps.get_model(app_label='courses', model_name=model_name)

        return None

    def get_form(self, model, *args, **kwargs):
        form = modelform_factory(model=model, exclude=['owner', 'order', 'created', 'updated'])
        return form(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.module = get_object_or_404(Module, id=kwargs['module_id'], course__owner=request.user)
        self.model = self.get_model(kwargs['model_name'])

        if kwargs.get('id'):
            self.content_obj = get_object_or_404(self.model, id=kwargs['id'], owner=request.user)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.get_form(self.model, instance=self.content_obj)
        return self.render_to_response(context={'form': form, 'object': self.content_obj, 'module': self.module})

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.model, instance=self.content_obj, data=request.POST, files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()

            if not kwargs.get('id'):
                Content.objects.create(module=self.module, item=obj)
                return redirect('module_content_list', self.module.id)
            else:
                return redirect('module_content_list', self.module.id)


        return self.render_to_response(context={'form': form, 'object': self.content_obj})


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user)
        module = content.module

        content.item.delete()
        content.delete()

        return redirect('module_content_list', module.id)


# class ModuleContentListView(TemplateResponseMixin, View):
#     template_name = 'courses/manage/module/content_list.html'
#
#     def get(self, request, module_id):
#         module = get_object_or_404(Module, id=module_id, course__owner=request.user)
#         modules = Module.objects.filter(id=module_id, course__owner=request.user).annotate(
#             total_contents=Count('contents'))
#         return self.render_to_response(context={'module': module, 'modules': modules})


class ModuleContentListView(ListView):
    template_name = 'courses/manage/module/content_list.html'
    context_object_name = 'module'

    def get_queryset(self):
        return get_object_or_404(Module, id=self.kwargs['module_id'], course__owner=self.request.user)


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):

    def post(self, request):
        for module_id, order in self.request_json.items():
            Module.objects.filter(id=module_id, course__owner=request.user).update(order=order)

        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):

    def post(self, request):
        for content_id, order in self.request_json.items():
            Content.objects.filter(id=content_id, module__course__owner=request.user).update(order=order)

        return self.render_json_response({'saved': 'OK'})


class CourseListView(TemplateResponseMixin, View):
    template_name = 'courses/course/list.html'
    model = Course

    def get(self, request, subject=None):
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(total_courses=Count('courses'))
            cache.set('all_subjects', subjects)
            logger.info('Subjects all_subjects added to cache')

        all_courses = Course.objects.annotate(total_modules=Count('modules'))

        if subject:
            subject = get_object_or_404(Subject, slug=subject)

            key = f"subject_{subject.id}_courses"
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject).order_by('-created')
                cache.set(key, courses)
                logger.info(f"Filtered courses {key} added to cache")
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses', courses)
                logger.info("Courses all_courses added to cache")

        return self.render_to_response({'subjects': subjects, 'courses': courses, 'subject': subject})


class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(initial={'course': self.object})
        return context
