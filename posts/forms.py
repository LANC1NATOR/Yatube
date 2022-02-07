from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('group', 'text', 'image')
        labels = {'text': 'Введите текст', 'group': 'Выберите группу',
                  'image': 'Вставьте изображение'}
        widgets = {'text': forms.Textarea()}


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)
        labels = {'text': 'Введите текст'}

