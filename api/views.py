from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from .permissions import OwnResourcePermission
from .serializers import PostSerializer, CommentSerializer
from posts.models import Post, Comment


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [OwnResourcePermission]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [OwnResourcePermission]
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        post = Post.objects.get(id=self.kwargs.get('post_pk'))
        serializer.save(author=self.request.user,
                        post=post)

    def get_queryset(self):
        post = get_object_or_404(Post, id=self.kwargs.get('post_pk'))
        return post.comments.all()


