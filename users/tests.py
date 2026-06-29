from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course
from users.models import Subscription, User


class SubscriptionTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="12345"
        )
        self.client.force_authenticate(user=self.user)
        self.course = Course.objects.create(name="test", description="test")

    def test_subscribe(self):
        response = self.client.post(
            reverse("users:user_subscribe"), {"course_id": self.course.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_unsubscribe(self):
        Subscription.objects.create(user=self.user, course=self.course)
        response = self.client.post(
            reverse("users:user_subscribe"), {"course_id": self.course.id}
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Subscription.objects.filter(user=self.user, course=self.course).exists()
        )

    def test_subscribe_with_invalid_course_id(self):
        response = self.client.post(
            reverse("users:user_subscribe"), {"course_id": 9999}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_subscribe_without_authentication(self):
        self.client.logout()  # Убираем аутентификацию
        response = self.client.post(
            reverse("users:user_subscribe"), {"course_id": self.course.id}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
