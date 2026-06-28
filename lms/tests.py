from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from lms.models import Course, Lesson
from users.models import User


class LessonTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='12345')
        self.user.is_staff = True
        self.user.save()
        self.lesson = Lesson.objects.create(
            name='test',
            description='test',
            owner=self.user
        )
        self.client.force_authenticate(user=self.user)

    def test_getting_lesson_list(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse('lms:lesson_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_lesson(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(reverse('lesson_create'), {
            'name': 'new lesson', 'description': 'new description'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Lesson.objects.filter(name='test').exists())

    def test_update_lesson(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(reverse('lms:lesson_update', kwargs={'pk': self.lesson.id}), {
            'name': 'updated lesson', 'description': 'updated description'
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(Lesson.objects.filter(name='updated lesson').exists())

    def test_destroy_lesson(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(reverse('lesson_delete', kwargs={'pk': self.lesson.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson.id).exists())


class CourseTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='testuser@example.com', password='12345')
        self.client.force_authenticate(user=self.user)
        self.course = Course.objects.create(name='test', description='test')

    def test_getting_course_list(self):
        response = self.client.get(reverse('course-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        expected_data = [
            {
                'id': self.course.id,
                'name': self.course.name,
                'description': self.course.description,
            }
        ]
        self.assertEqual(response.json(), expected_data)
