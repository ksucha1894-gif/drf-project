from rest_framework.serializers import ModelSerializer, SerializerMethodField

from .models import Course, Lesson


class CourseSerializer(ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"


class LessonSerializer(ModelSerializer):
    class Meta:
        model = Lesson
        fields = "__all__"


class CourseDetailSerializer(ModelSerializer):
    lessons_count = SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    def get_lessons_count(self, obj):
        if obj.lessons.count():
            return obj.lessons.count()
        return 0

    class Meta:
        model = Course
        fields = ("name", "image", "description", "lessons_count", "lessons")
