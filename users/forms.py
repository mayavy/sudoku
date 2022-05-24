import email
from django import forms
from .models import CustomUser
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm


class PwdChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'change-pwd'}))
    new_password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'New password', 'id': 'change-pwd'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Confirm new password', 'id': 'change-pwd'}))


class PwdResetConfirmForm(SetPasswordForm):  # using same ele id as above
    new_password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'New password', 'id': 'change-pwd'}))
    new_password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Confirm new password', 'id': 'change-pwd'}))


class PwdResetForm(PasswordResetForm):
    email = forms.EmailField(max_length=254, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter email', 'id': 'login-email'}))

    def clean_email(self):
        email = self.cleaned_data['email']
        exist = CustomUser.objects.filter(email=email)
        if not exist:
            raise forms.ValidationError(
                "you never registered")
        return email


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Username', 'id': 'login-username'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'placeholder': 'Password', 'id': 'login-pwd'}))


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(
        label='Username', min_length=3, max_length=40, help_text='I command you',
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Enter username', 'id': 'login-username'}))

    email = forms.EmailField(label='Email',
                             max_length=100,
                             widget=forms.TextInput(
                                 attrs={'class': 'form-control', 'placeholder': 'Enter email', 'id': 'login-email'}))
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Password', 'id': 'login-pwd'}))

    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Repeat password', 'id': 'login-pwd'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email')

        def clean_username(self):
            username = self.cleaned_data['username'].lower()
            r = CustomUser.objects.filter(username=username)
            if r.count():
                raise ValidationError("Nah! use some one already have that")
            return username

        def clean_password2(self):
            cd = self.cleaned_data
            if cd['password1'] != cd['password2']:
                raise forms.ValidationError('passwords do not match')
            return cd['password2']

        def clean_email(self):
            email = self.cleaned_data['email']
            if CustomUser.objects.filter(email=email).exist():
                raise ValidationError(
                    "Nah! use some one already have that email")
            return email

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)


class UserEditForm(forms.ModelForm):  # not in use
    email = forms.EmailField(max_length=250)

    class Meta:
        model = CustomUser
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError('change email, unavilabel !')
        return email

    def __ini__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
