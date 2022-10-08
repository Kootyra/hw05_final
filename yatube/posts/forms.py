from django import forms
from django.core.exceptions import ValidationError

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image',)
        labels = {'text': 'Введите текст.',
                  'group': 'Выберите группу.',
                  'image': 'Вы можете добавить картинку'}
        help_texts = {'text': 'Текст нового поста.',
                      'group': 'Группа, к которой будет относиться пост.',
                      'image': 'Загрузите изображение'}

    def clean_text(self):
        data = self.cleaned_data['text']
        if not data:
            raise ValidationError('Введите текст поста!')
        return data


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Введите текст.'}
        help_texts = {'text': 'Текст нового комментария.'}
