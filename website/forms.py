from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils import timezone
from .models import User, Appointment

# === 1. Форма для записи на приём (Appointment) ===
class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = [
            'client',
            'master',
            'service',
            'appointment_date',
            'appointment_time',
            'status'
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'master': forms.Select(attrs={'class': 'form-select'}),
            'service': forms.Select(attrs={'class': 'form-select'}),
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned = super().clean()
        # Бизнес-логика — в модели Appointment.clean()
        return cleaned


# === 2. Форма регистрации нового пользователя ===
class RegistrationForm(UserCreationForm):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        label='Роль',
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    password1 = forms.CharField(
        label='Пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Повторите пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

# === 3. Собственная форма входа, чтобы поля получили class="form-control" ===

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control custom-input',
            'placeholder': 'Имя пользователя'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control custom-input',
            'placeholder': 'Пароль'
        })
