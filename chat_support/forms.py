from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.forms import Textarea
from .models import User, RatingStar, Rating
from django.core.exceptions import ValidationError

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
    email = forms.CharField(label='Электронная почта', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password_1 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_1 = cleaned_data.get('password_1')
        if password != password_1:
            raise ValidationError('Пароли не совпадают')
        return self.cleaned_data


class RatingForm(forms.ModelForm):

    star_1 = forms.ModelChoiceField(label='Насколько быстро ответили на Ваш вопрос?',
        queryset=RatingStar.objects.all(), widget=forms.RadioSelect(attrs={'class':'selector'}), empty_label=None,

    )
    star_2 = forms.ModelChoiceField(label='Получили ли вы ответ на свой вопрос?',
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
