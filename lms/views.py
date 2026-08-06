from django.utils.decorators import method_decorator
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from lms.models import Course, Lesson
from lms.paginators import MyPagination
from lms.tasks import send_latest_update, send_moderator_email
from users.models import Subscription
from users.permissions import IsModer, IsOwner

from .serializers import (CourseDetailSerializer, CourseSerializer,
                          LessonSerializer)

from users.services import create_stripe_product, create_stripe_price, create_stripe_session
from lms.models import Course, Lesson, Subscription


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_description="description from swagger_auto_schema via method_decorator"
    ),
)
class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    filter_backends = [filters.OrderingFilter]
    filterset_fields = ("course", "lesson", "payment_method")
    pagination_class = MyPagination

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        course = serializer.save()
        course.owner = self.request.user
        course.save()
        # Получаем всех подписчиков курса
        subscribers = Subscription.objects.filter(course=course)
        emails = [sub.user.email for sub in subscribers]
        # Запускаем задачу Celery для отправки писем
        if emails:
            send_moderator_email.delay(course.id)

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = (~IsModer,)
        elif self.action in ["update", "retrieve"]:
            self.permission_classes = (IsModer, IsAuthenticated, IsOwner)
        elif self.action == "destroy":
            self.permission_classes = (IsOwner, IsAuthenticated)
        return super().get_permissions()

    def get_queryset(self):
        return Course.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        course = serializer.save()
        # Получаем всех подписчиков курса
        subscribers = Subscription.objects.filter(course=course)
        emails = [sub.user.email for sub in subscribers]
        # Запускаем задачу Celery для отправки писем
        if emails:
            send_moderator_email.delay(course.id)

    @action(detail=True, methods=['post'])
    def payment(self, request, pk=None):
        """Эндпоинт для генерации ссылки на оплату курса через Stripe."""
        course = self.get_object()
        unit_amount = 500000  # 5000 рублей в копейках
        product = create_stripe_product(name=course.title, description=course.description)
        price = create_stripe_price(product_id=product.id, unit_amount=unit_amount)
        session = create_stripe_session(price_id=price.id)
        return Response({
            "course": course.title,
            "amount": unit_amount / 100,
            "payment_url": session.url,
            "session_id": session.id
        })


class LessonCreateApiView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    @swagger_auto_schema(
        operation_description="Создание нового урока",
        request_body=LessonSerializer,
        responses={201: LessonSerializer, 400: openapi.Response("Ошибка валидации")},
    )
    def perform_create(self, serializer):
        lesson = serializer.save()
        lesson.owner = self.request.user
        lesson.save()
        subscribers = Subscription.objects.filter(course=lesson.course)
        emails = [sub.user.email for sub in subscribers]
        # Запускаем задачу Celery для отправки писем
        if emails:
            send_moderator_email.delay(course.id)

    def get_permissions(self):
        self.permission_classes = [~IsModer, IsAuthenticated]
        return super().get_permissions()


class LessonListApiView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = MyPagination

    @swagger_auto_schema(
        operation_description="Получение списка уроков",
        responses={
            200: LessonSerializer(many=True),
            404: openapi.Response("Не найдено"),
        },
    )
    def get_permissions(self):
        self.permission_classes = [IsModer, IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        return Lesson.objects.filter(owner=self.request.user)


class LessonRetrieveApiView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    @swagger_auto_schema(
        operation_description="Получение данных урока",
        responses={200: LessonSerializer, 404: openapi.Response("Не найдено")},
    )
    def get_permissions(self):
        self.permission_classes = [IsModer, IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        return Lesson.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        lesson = serializer.save()
        # Получаем всех подписчиков курса
        subscribers = Subscription.objects.filter(course=lesson.course)
        emails = [sub.user.email for sub in subscribers]
        # Запускаем задачу Celery для отправки писем
        if emails:
            send_latest_update.delay(course.id)


class LessonUpdateApiView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    @swagger_auto_schema(
        operation_description="Изменение уроков",
        request_body=LessonSerializer,
        responses={200: LessonSerializer, 400: openapi.Response("Ошибка валидации")},
    )
    def get_permissions(self):
        self.permission_classes = [IsModer | IsOwner, IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        return Lesson.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        lesson = serializer.save()
        # Получаем всех подписчиков курса
        subscribers = Subscription.objects.filter(course=lesson.course)
        emails = [sub.user.email for sub in subscribers]
        # Запускаем задачу Celery для отправки писем
        if emails:
            send_latest_update.delay(course.id)


class LessonDestroyApiView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    @swagger_auto_schema(
        operation_description="Изменение уроков",
        responses={201: LessonSerializer, 400: openapi.Response("Ошибка валидации")},
    )
    def get_permissions(self):
        self.permission_classes = [IsOwner, IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        return Lesson.objects.filter(owner=self.request.user)
