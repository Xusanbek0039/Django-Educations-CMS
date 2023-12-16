from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings

from courses.fields import OrderField
from django.template.loader import render_to_string


class Subject(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='courses_created', on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, related_name='courses', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='courses_joined', blank=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.order}.{self.title}"


class Content(models.Model):
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': ('text', 'video', 'image', 'file')})
    object_id = models.PositiveBigIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']


class ItemBase(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def render(self):
        return render_to_string(f"courses/content/{self._meta.model_name}.html", {'item':self})

    def to_json(self):
        return ''


class Text(ItemBase):
    content = models.TextField()

    def to_json(self):
        return self.content


class File(ItemBase):
    content = models.FileField(upload_to='files')

    def to_json(self):
        return self.content.url


class Image(ItemBase):
    content = models.ImageField(upload_to='images')

    def to_json(self):
        return self.content.url


class Video(ItemBase):
    content = models.URLField()

    def to_json(self):
        return self.content
