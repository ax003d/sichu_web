from django import forms
from django.contrib.auth.models import User

from oauth2app.models import Client

from cabinet.models import BookBorrowRequest


class BookBorrowRequestForm(forms.ModelForm):
    class Meta:
        model = BookBorrowRequest
        exclude = ('datetime', 'status')


class LoginForm(forms.Form):
    username   = forms.CharField()
    password   = forms.CharField()
    apikey     = forms.CharField()

    def clean(self):
        try:
            client = Client.objects.get(key=self.data.get('apikey'))
            user = User.objects.get(username=self.data.get('username'))
            if not user.check_password(self.data.get('password')):
                raise forms.ValidationError("Password error!")            
            return self.cleaned_data
        except Client.DoesNotExist:
            raise forms.ValidationError("API Key error!")
        except User.DoesNotExist:
            raise forms.ValidationError("User does not exist!")


class RegisterForm(forms.ModelForm):
    apikey = forms.CharField()
    class Meta:
        model = User
        exclude = ('last_login', 'date_joined')

    def clean_apikey(self):
        try:
            apikey = self.cleaned_data['apikey']
            client = Client.objects.get(key=apikey)
            return apikey
        except Client.DoesNotExist:
            raise forms.ValidationError("API Key error!")

    def clean_username(self):
        try:
            username = self.cleaned_data['username']
            user = User.objects.get(username=username)
            raise forms.ValidationError("username not available!")
        except User.DoesNotExist:
            return username

    def clean_email(self):
        try:
            email = self.cleaned_data['email']
            user = User.objects.get(email=email)
            raise forms.ValidationError("email not available!")
        except User.DoesNotExist:
            return email
