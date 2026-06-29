from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson
from users.models import User


class LessonTestCase(APITestCase):
    def setUp(self):
        # Создаем группу модераторов
        self.moder_group, created = Group.objects.get_or_create(name="moders")

        # Создаем пользователя и модератора
        self.user = User.objects.create_user(
            email="testuser@example.com", password="12345"
        )
        self.moder = User.objects.create_user(
            email="moduser@example.com", password="12345"
        )
        self.moder.groups.add(self.moder_group)  # Добавляем в группу модераторов

        # Создаем курс и урок
        self.course = Course.objects.create(name="test course", description="test")
        self.lesson = Lesson.objects.create(
            name="test", description="test", course=self.course, owner=self.user
        )

    def test_getting_lesson_list_as_moderator(self):
        # Аутентифицируем модератора
        self.client.force_authenticate(user=self.moder)
        response = self.client.get(reverse("lms:lesson_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_getting_lesson_list_as_authenticated_user(self):
        # Аутентифицируем обычного пользователя
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("lms:lesson_list"))
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )  # Ожидаем 403, т.к. не модератор

    def test_create_lesson_as_authenticated_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("lms:lesson_create"),
            {
                "name": "new lesson",
                "description": "new description",
                "course": self.course.id,
            },
        )
        self.assertEqual(
            response.status_code, status.HTTP_201_CREATED
        )  # Ожидаем 201, т.к. пользователь аутентифицирован

    def test_create_lesson_as_moderator(self):
        self.client.force_authenticate(user=self.moder)
        response = self.client.post(
            reverse("lms:lesson_create"),
            {
                "name": "new lesson",
                "description": "new description",
                "course": self.course.id,
            },
        )
        self.assertEqual(
            response.status_code, status.HTTP_403_FORBIDDEN
        )  # Ожидаем 403, т.к. модератор не может создавать уроки


class CourseTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="12345"
        )
        self.client.force_authenticate(user=self.user)
        # Устанавливаем владельца курса
        self.course = Course.objects.create(
            name="test", description="test", owner=self.user
        )
        self.assertTrue(
            Course.objects.filter(id=self.course.id, owner=self.user).exists()
        )

    def test_getting_course_list(self):
        response = self.client.get(reverse("lms:course-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                "id": self.course.id,
                "name": self.course.name,
                "description": self.course.description,
                "image": None,  # или изображение, если оно есть
                "owner": self.user.id,  # Идентификатор владельца
            }
        ]
        # Сравниваем только результаты
        self.assertEqual(response.json()["results"], expected_data)

    def test_access_rights_for_different_users(self):
        # Пример для обычного пользователя
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse("users:user_subscribe"), {"course_id": self.course.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Пример для неавторизованного пользователя
        self.client.logout()
        response = self.client.post(
            reverse("users:user_subscribe"), {"course_id": self.course.id}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
