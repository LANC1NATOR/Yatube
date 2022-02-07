from rest_framework import serializers

from posts.models import Post, Comment, Group, Follow


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = ['id', 'text', 'author',  'pub_date']


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')
    post = serializers.ReadOnlyField(source='post.id')

    class Meta:
        model = Comment
        fields = ['id', 'author', 'text', 'created', 'post']


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ['title']


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username', read_only=True)
    author = serializers.CharField(source='author.username')

    class Meta:
        model = Follow
        fields = ['user', 'author']