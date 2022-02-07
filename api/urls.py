from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PostViewSet, CommentViewSet, GroupViewSet, FollowViewSet

from rest_framework_simplejwt.views import (
        TokenObtainPairView,
        TokenRefreshView,
    )

router = DefaultRouter()
router.register('v1/posts', PostViewSet)
router.register(r'v1/posts/(?P<post_pk>\d+)/comments', CommentViewSet)
router.register('v1/groups', GroupViewSet)
router.register('v1/follow', FollowViewSet)

urlpatterns = [
    path('v1/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('v1/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('', include(router.urls)),
]
