from django.forms.models import inlineformset_factory
from courses.models import Course, Module
from django.forms.models import inlineformset_factory

from courses.models import Course, Module

ModuleFormset = inlineformset_factory(Course, Module, fields=('title', 'description'), extra=2, can_delete=True)
