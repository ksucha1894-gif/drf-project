from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
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
from users.services import create_stripe_price, create_stripe_session

from .serializers import PaymentSerializer, UserSerializer


# class PaymentViewSet(ModelViewSet):
#     queryset = Payment.objects.all()
#     filter_backends = [filters.OrderingFilter]
#     filterset_fields = ("user", "course", "lesson", "payment_method")
#     ordering_fields = ("payment_date",)
#
#     @swagger_auto_schema(
#         operation_description="Получение списка платежей",
#         responses={200: PaymentSerializer(many=True)},
#     )
#     def list(self, request, *args, **kwargs):
#         return super().list(request, *args, **kwargs)


class PaymentCreateApiView(CreateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @swagger_auto_schema(
        operation_description="Создание платежа",
        request_body=PaymentSerializer,
        responses={201: PaymentSerializer, 400: openapi.Response("Ошибка валидации")},
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(user=self.request.user)

        try:
            product = create_stripe_product("Product Name", "Product Description")
            payment.stripe_product_id = product.id
            payment.save()

            unit_amount = int(payment.amount * 100)
            price = create_stripe_price(payment.stripe_product_id, unit_amount)
            payment.stripe_price_id = price.id  # Сохраняем цену

            stripe_session = create_stripe_session(price.id)
            payment.stripe_session_id = stripe_session.id
            payment.link = stripe_session.url
            payment.save()

            return Response(
                {"payment_link": payment.link, **serializer.data}, status=201
            )
        except stripe.error.StripeError as e:
            return Response({"error": str(e)}, status=500)


class PaymentListApiView(ListAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @swagger_auto_schema(
        operation_description="Получение списка платежей",
        responses={
            200: PaymentSerializer(many=True),
            404: openapi.Response("Не найдено"),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PaymentRetrieveApiView(RetrieveAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @swagger_auto_schema(
        operation_description="Изменение платежей",
        request_body=PaymentSerializer,
        responses={201: PaymentSerializer, 400: openapi.Response("Ошибка валидации")},
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PaymentUpdateApiView(UpdateAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @swagger_auto_schema(
        operation_description="Изменение платежей",
        request_body=PaymentSerializer,
        responses={200: PaymentSerializer, 400: openapi.Response("Ошибка валидации")},
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class PaymentDestroyApiView(DestroyAPIView):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    @swagger_auto_schema(
        operation_description="Изменение платежей",
        responses={204: PaymentSerializer, 400: openapi.Response("Ошибка валидации")},
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class PaymentStatusApiView(APIView):

    @swagger_auto_schema(
        operation_description="Проверка платежей",
        responses={200: PaymentSerializer, 400: openapi.Response("Ошибка валидации")},
    )
    def get(self, request, *args, **kwargs):
        stripe_session_id = request.query_params.get("stripe_session_id")
        if not stripe_session_id:
            return Response({"error": "stripe_session_id is required"}, status=400)

        try:
            session = stripe.checkout.Session.retrieve(stripe_session_id)
            payment = Payment.objects.get(stripe_session_id=stripe_session_id)
            payment.status = session.status
            payment.save()
            return Response({"status": payment.status}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class UserCreateApiView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        operation_description="Создание пользователя",
        request_body=UserSerializer,
        responses={201: UserSerializer, 400: openapi.Response("Ошибка валидации")},
    )
    def perform_create(self, serializer):
        user = serializer.save()  # Сохраняем пользователя без параметра is_active
        user.is_active = True  # Теперь мы отдельно устанавливаем is_active
        user.set_password(user.password)
        user.save()


class UserListApiView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Просмотр пользователей",
        request_body=UserSerializer,
        responses={201: UserSerializer, 400: openapi.Response("Ошибка валидации")},
    )
    def get_permissions(self):
        self.permission_classes = [
            IsAuthenticated,
        ]
        return super().get_permissions()


class UserRetrieveApiView(RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Получение данных пользователя",
        responses={200: UserSerializer, 404: openapi.Response("Не найдено")},
    )
    def get_permissions(self):
        self.permission_classes = [
            IsAuthenticated,
        ]
        return super().get_permissions()


class UserUpdateApiView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Изменение пользователя",
        request_body=UserSerializer,
        responses={200: UserSerializer, 400: openapi.Response("Ошибка валидации")},
    )
    def get_permissions(self):
        self.permission_classes = [
            IsAuthenticated,
        ]
        return super().get_permissions()


class UserDestroyApiView(DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Удаление пользователя",
        responses={204: UserSerializer, 400: openapi.Response("Ошибка валидации")},
    )
    def get_permissions(self):
        self.permission_classes = [
            IsAuthenticated,
        ]
        return super().get_permissions()


class SubscriptionAPIView(APIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @swagger_auto_schema(
        operation_description="Проверяем подписку пользователя",
        manual_parameters=[
            openapi.Parameter(
                "course_id",
                openapi.IN_QUERY,
                description="ID курса",
                type=openapi.TYPE_INTEGER,
            )
        ],
        responses={200: "Успешно", 400: "Ошибка валидации"},
    )
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
