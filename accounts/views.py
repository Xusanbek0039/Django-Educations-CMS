from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import Group
from django.views.generic.edit import CreateView

from accounts.forms import CustomUserRegistrationForm
import logging

logger = logging.getLogger(__name__)


class UserRegistrationView(CreateView):
    form_class = CustomUserRegistrationForm
    template_name = 'registration/registration.html'
    success_url = settings.LOGIN_REDIRECT_URL

    def form_valid(self, form):
        result = super().form_valid(form)
        cd = form.cleaned_data

        user = authenticate(username=cd['email'], password=cd['password1'])
        login(self.request, user)

        # add instructor user to Instructor group
        if cd['is_instructor']:
            try:
                instructor_group = Group.objects.get(name='Instructors')
                self.request.user.groups.add(instructor_group)
                logger.info(f'User {self.request.user.email} registered as Instructor')
            except Group.DoesNotExist:
                logger.error('Instructors group does not exist')

        return result
