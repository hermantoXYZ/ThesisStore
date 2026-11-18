from django import forms
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User


class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if not User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Alamat email tidak terdaftar di sistem kami.")
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("Akun dengan alamat email ini berstatus tidak aktif.")
        return email