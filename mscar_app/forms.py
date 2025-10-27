from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['author_name', 'rating', 'text']
        widgets = {
            'author_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ваше имя'
            }),
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
            'author_name': 'Имя',
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