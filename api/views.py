from django.shortcuts import get_object_or_404
from rest_framework import viewsets, filters
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from .permissions import IsAuthorOrAdminOrReadOnly, IsAdminOrReadOnly
from .serializers import PostSerializer, CommentSerializer, GroupSerializer, \
    FollowSerializer
from posts.models import Post, Comment, Group, Follow, User


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly, IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filter_fields = ['group']

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthorOrAdminOrReadOnly, IsAuthenticated]
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        post = Post.objects.get(id=self.kwargs.get('post_pk'))
        serializer.save(author=self.request.user,
                        post=post)

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs.get('post_pk'))
        return post.comments.all()


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminOrReadOnly,
                          IsAuthenticated]


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    queryset = Follow.objects.all()
    permission_classes = [IsAuthorOrAdminOrReadOnly, IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=author__username',
                     '=user__username']

    def perform_create(self, serializer):
        author = get_object_or_404(
            User, username=self.request.data.get("author")
        )
        user = self.request.user
        follows = self.queryset.filter(user=user, author=author)
        if follows.exists():
            raise ValidationError(
                f"You already have a subscription to {author}.")
        if user == author:
            raise ValidationError("You cannot subscribe to yourself.")
        serializer.save(user=user, author=author)


