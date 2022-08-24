from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
# from django.contrib.auth.models import User
from django.forms import Textarea
from django.utils.safestring import mark_safe
from .models import User, RatingStar, Rating


class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Табельный номер', widget=forms.TextInput(attrs={'class': 'form-input'})),
    email = forms.EmailField(label='Электронная почта', widget=forms.EmailInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widdets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-input'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-input'}),
        }


class PasswordReset(forms.Form):
    username = forms.CharField(label='Табельный номер', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password_1 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

class RatingForm(forms.ModelForm):

    star_1 = forms.ModelChoiceField(label='Оценка скорости обслуживания',
        queryset=RatingStar.objects.all(), widget=forms.RadioSelect(attrs={'class':'selector'}), empty_label=None,

    )
    star_2 = forms.ModelChoiceField(label='Оценка еще чего-то',
        queryset=RatingStar.objects.all(), widget=forms.RadioSelect(attrs={'class':'selector'}), empty_label=None,

    )
    # star_3 = forms.ModelChoiceField(
    #     queryset=RatingStar.objects.all(), widget=forms.RadioSelect(attrs={'class':'selector'}), empty_label=None,
    #
    # )
    comment = forms.CharField(label='Оставьте комментарии', widget=Textarea(attrs={'rows': 3}))

    class Meta:
        model = Rating
        fields = ("star_1", "star_2", 'comment', )


class StaffForm(forms.Form):
    username = forms.IntegerField(label='Табельный номер', widget=forms.TextInput(attrs={'class': 'form-input'}))

