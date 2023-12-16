from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from accounts.models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['email']


class CustomUserRegistrationForm(UserCreationForm):
    is_instructor = forms.BooleanField(label='Are you an instructor?', required=False)

    class Meta:
        model = User
        fields = ['email']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_instructor = self.cleaned_data['is_instructor']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['email']
