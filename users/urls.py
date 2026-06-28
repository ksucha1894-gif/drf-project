from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.apps import UsersConfig
from users.views import (
    PaymentCreateApiView,
    PaymentDestroyApiView,
    PaymentListApiView,
    PaymentRetrieveApiView,
    PaymentUpdateApiView,
    PaymentViewSet,
    SubscriptionAPIView,
    UserCreateApiView,
    UserDestroyApiView,
    UserListApiView,
    UserRetrieveApiView,
    UserUpdateApiView,
)

app_name = UsersConfig.name

routers = SimpleRouter()
routers.register(r"payment", PaymentViewSet)

urlpatterns = [
    path("payment/", PaymentListApiView.as_view(), name="payment_list"),
    path(
        "payment/<int:pk>/", PaymentRetrieveApiView.as_view(), name="payment_retrieve"
    ),
    path("payment/create/", PaymentCreateApiView.as_view(), name="payment_create"),
    path(
        "payment/<int:pk>/delete/",
        PaymentDestroyApiView.as_view(),
        name="payment_delete",
    ),
    path(
        "payment/<int:pk>/update/",
        PaymentUpdateApiView.as_view(),
        name="payment_update",
    ),
    path("register/", UserCreateApiView.as_view(), name="register"),
    path(
        "login/",
        TokenObtainPairView.as_view(permission_classes=(AllowAny,)),
        name="login",
    ),
    path(
        "token/refresh/",
        TokenRefreshView.as_view(permission_classes=(AllowAny,)),
        name="token_refresh",
    ),
    path("user/", UserListApiView.as_view(), name="user_list"),
    path("user/<int:pk>/", UserRetrieveApiView.as_view(), name="user_retrieve"),
    path("user/create/", UserCreateApiView.as_view(), name="user_create"),
    path(
        "user/<int:pk>/delete/",
        UserDestroyApiView.as_view(),
        name="user_delete",
    ),
    path("user/<int:pk>/update/", UserUpdateApiView.as_view(), name="user_update"),
    path("user/subscribe/", SubscriptionAPIView.as_view(), name="user_subscribe"),
]

urlpatterns += routers.urls
