from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review, Mod, Version, UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-input',
        'placeholder': 'Email'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Имя пользователя'
            }),
        }

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'website']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Расскажите о себе...',
                'rows': 4
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://example.com'
            }),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'text']
        widgets = {
            'rating': forms.Select(attrs={
                'class': 'form-select'
            }),
            'text': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Ваш отзыв...',
                'rows': 4
            }),
        }
        labels = {
            'rating': 'Оценка',
            'text': 'Отзыв'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget.choices = [
            (1, '★ 1 - Ужасно'),
            (2, '★★ 2 - Плохо'),
            (3, '★★★ 3 - Нормально'),
            (4, '★★★★ 4 - Хорошо'),
            (5, '★★★★★ 5 - Отлично')
        ]

class ModForm(forms.ModelForm):
    class Meta:
        model = Mod
        fields = ['title', 'description', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Название мода'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Описание мода...',
                'rows': 6
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        labels = {
            'title': 'Название',
            'description': 'Описание',
            'category': 'Категория',
            'image': 'Изображение мода'
        }

class VersionForm(forms.ModelForm):
    class Meta:
        model = Version
        fields = ['version_number', 'release_date', 'changelog', 'file']
        widgets = {
            'version_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '1.0.0'
            }),
            'release_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'changelog': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Список изменений в этой версии...',
                'rows': 4
            }),
        }