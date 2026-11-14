from allauth.account.forms import SignupForm, LoginForm
from django import forms
from django.core.exceptions import ValidationError
from .models import User
import re

class CustomSignupForm(SignupForm):
    full_name = forms.CharField(max_length=100, label='Full Name')
    phone = forms.CharField(max_length=15, required=False, label='Phone Number')

    def save(self, request):
        user = super().save(request)
        user.full_name = self.cleaned_data['full_name']
        user.phone = self.cleaned_data.get('phone', '')
        user.save()
        return user

class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['login'].label = 'Email or Phone'
        self.fields['login'].widget.attrs.update({'placeholder': 'Email or 0803...'})
    def clean_login(self):
        login = self.cleaned_data.get('login', '').strip()
        if re.match(r'^[+\d][\d\s-]{9,15}$', login):
            phone = re.sub(r'\D', '', login)
            try:
                user = User.objects.get(phone=phone)
                return user.email
            except User.DoesNotExist:
                raise ValidationError("No account with this phone number.")
        return login.lower()