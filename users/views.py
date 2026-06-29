from django.shortcuts import get_object_or_404
from rest_framework import filters, status
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from lms.models import Course
from users.models import Payment, Subscription, User

from .serializers import PaymentSerializer, UserSerializer


class PaymentViewSet(ModelViewSet):
    queryset = Payment.objects.all()
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ("user", "course", "lesson", "payment_method")
    ordering_fields = ("payment_date",)


class PaymentCreateApiView(CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentListApiView(ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentRetrieveApiView(RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentUpdateApiView(UpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class PaymentDestroyApiView(DestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class UserCreateApiView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()  # Сохраняем пользователя без параметра is_active
        user.is_active = True  # Теперь мы отдельно устанавливаем is_active
        user.set_password(user.password)
        user.save()


class UserListApiView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        self.permission_classes = [
            IsAuthenticated,
        ]
        return super().get_permissions()


class UserRetrieveApiView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        self.permission_classes = [
            IsAuthenticated,
        ]
        return super().get_permissions()


class UserUpdateApiView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        self.permission_classes = [
            IsAuthenticated,
        ]
        return super().get_permissions()


class UserDestroyApiView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        self.permission_classes = [
            IsAuthenticated,
        ]
        return super().get_permissions()


class SubscriptionAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):  # Добавляем self
        user = request.user  # Получаем текущего пользователя
        course_id = request.data.get("course_id")  # Получаем ID курса из запроса
        course_item = get_object_or_404(
            Course, id=course_id
        )  # Находим курс или возвращаем 404

        # Проверяем, есть ли уже подписка
        subs_item = Subscription.objects.filter(user=user, course=course_item)
        if subs_item.exists():
            # Если подписка есть, удаляем её
            subs_item.delete()
            message = "Подписка удалена"
            status_code = status.HTTP_204_NO_CONTENT
        else:
            # Если подписки нет, создаём её
            Subscription.objects.create(user=user, course=course_item)
            message = "Подписка добавлена"
            status_code = status.HTTP_201_CREATED

        # Возвращаем ответ
        return Response({"message": message}, status=status_code)
