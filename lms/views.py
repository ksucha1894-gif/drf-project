from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import filters
from rest_framework.generics import (CreateAPIView, DestroyAPIView,
                                     ListAPIView, RetrieveAPIView,
                                     UpdateAPIView)
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from lms.models import Course, Lesson
from lms.paginators import MyPagination
from users.permissions import IsModer, IsOwner

from .serializers import (CourseDetailSerializer, CourseSerializer,
                          LessonSerializer)


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

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        course = serializer.save()
        course.owner = self.request.user
        course.save()

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


class LessonCreateApiView(CreateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def perform_create(self, serializer):
        lesson = serializer.save()
        lesson.owner = self.request.user
        lesson.save()

    def get_permissions(self):
        self.permission_classes = [~IsModer, IsAuthenticated]
        return super().get_permissions()


class LessonListApiView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    pagination_class = MyPagination

    def get_permissions(self):
        self.permission_classes = [IsModer, IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        return Lesson.objects.filter(owner=self.request.user)


class LessonRetrieveApiView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        self.permission_classes = [IsModer, IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        return Lesson.objects.filter(owner=self.request.user)


class LessonUpdateApiView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        self.permission_classes = [IsModer | IsOwner, IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        return Lesson.objects.filter(owner=self.request.user)


class LessonDestroyApiView(DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer

    def get_permissions(self):
        self.permission_classes = [IsOwner, IsAuthenticated]
        return super().get_permissions()

    def get_queryset(self):
        return Lesson.objects.filter(owner=self.request.user)
