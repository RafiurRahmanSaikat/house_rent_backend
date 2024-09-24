from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AddFavorite,
    ChangePasswordView,
    EmailConfirmationView,
    RemoveFavorite,
    UpdateProfileView,
    UserInfoAPIView,
    UserLoginAPIView,
    UserLogoutAPIView,
    UserRegisterAPIView,
)

router = DefaultRouter()

urlpatterns = [
    path("register/", UserRegisterAPIView.as_view(), name="register"),
    path("login/", UserLoginAPIView.as_view(), name="login"),
    path("logout/", UserLogoutAPIView.as_view(), name="logout"),
    path("profile/", UserInfoAPIView.as_view(), name="user_info"),
    path("updateProfile/", UpdateProfileView.as_view(), name="update_profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change_password"),
    path(
        "profile/favorites/add/<int:ad_id>/",
        AddFavorite.as_view(),
        name="add_favorite",
    ),
    path(
        "profile/favorites/remove/<int:ad_id>/",
        RemoveFavorite.as_view(),
        name="remove_favorite",
    ),
    path(
        "active/<str:uid64>/<str:token>/",
        EmailConfirmationView.as_view(),
        name="email_confirm",
    ),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
