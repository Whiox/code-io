import os
import shutil
import tempfile
from unittest.mock import patch

from django.test import TestCase, Client, override_settings
from django.urls import reverse

from authentication.models import User
from education.models import Courses, Stars, Report


class AllCourseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_all_course_get(self):
        response = self.client.get(reverse('all'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'all_courses.html')


class StaredCoursesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_stared_view_get_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('stared'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stared_courses.html')

    def test_stared_view_get_anonymous(self):
        response = self.client.get(reverse('stared'))
        self.assertEqual(response.status_code, 302)


class MyCoursesViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_my_view_get_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('my_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_courses.html')

    def test_my_view_get_anonymous(self):
        response = self.client.get(reverse('my_courses'))
        self.assertEqual(response.status_code, 302)


class CreateCourseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_create_view_get_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('add_course'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_course.html')

    def test_create_view_get_anonymous(self):
        response = self.client.get(reverse('add_course'))
        self.assertEqual(response.status_code, 302)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ViewCourseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='u@e.com', username='u', password='p')
        self.course = Courses.objects.create(title='Test', author=self.user)
        self.course_id = self.course.course_id

    def tearDown(self):
        shutil.rmtree(self._get_media_root(), ignore_errors=True)

    def _get_media_root(self):
        return os.environ.get('DJANGO_TEST_TEMP_MEDIA_ROOT') or tempfile.gettempdir()

    def test_get_nonexistent_dir(self):
        url = reverse('course', args=[self.course_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'error.html')
        self.assertIn('Курс не найден.', response.context['error'])


class DeleteCourseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='u@e.com', username='u', password='p')
        self.other = User.objects.create_user(email='o@e.com', username='o', password='p')
        self.course = Courses.objects.create(title='Del', author=self.user)
        self.course_id = self.course.course_id
        self.media = tempfile.mkdtemp()
        self.patch = override_settings(MEDIA_ROOT=self.media)
        self.patch.enable()
        os.makedirs(os.path.join(self.media, str(self.course_id)), exist_ok=True)

    def tearDown(self):
        self.patch.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def test_get_not_author(self):
        self.client.login(email='o@e.com', password='p')
        url = reverse('delete', args=[self.course_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'error.html')

    def test_get_author(self):
        self.client.login(email='u@e.com', password='p')
        url = reverse('delete', args=[self.course_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirm_delete.html')

    def test_post_not_author(self):
        self.client.login(email='o@e.com', password='p')
        url = reverse('delete', args=[self.course_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'error.html')

    def test_post_author(self):
        self.client.login(email='u@e.com', password='p')
        url = reverse('delete', args=[self.course_id])
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('my_courses'))
        self.assertFalse(Courses.objects.filter(course_id=self.course_id).exists())
        self.assertFalse(os.path.exists(os.path.join(self.media, str(self.course_id))))

class AddStarViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='u@e.com', username='u', password='p')
        self.course = Courses.objects.create(title='Star', author=self.user)
        self.course_id = self.course.course_id

    def test_post_anonymous(self):
        url = reverse('add_star', args=[self.course_id])
        response = self.client.post(url)
        self.assertEqual(response.json()['status'], False)

    def test_post_toggle(self):
        self.client.login(email='u@e.com', password='p')
        url = reverse('add_star', args=[self.course_id])
        res1 = self.client.post(url)
        self.assertTrue(res1.json()['status'])
        self.assertTrue(Stars.objects.filter(user=self.user, course=self.course).exists())
        res2 = self.client.post(url)
        self.assertFalse(res2.json()['status'])
        self.assertFalse(Stars.objects.filter(user=self.user, course=self.course).exists())

class ReportCourseViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(email='u@e.com', username='u', password='p')
        self.course = Courses.objects.create(title='Rpt', author=self.user)
        self.course_id = self.course.course_id
        self.client.login(email='u@e.com', password='p')

    def test_get(self):
        url = reverse('course_report', args=[self.course_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'report_course.html')
        self.assertIn('course', response.context)

    def test_post_no_reason(self):
        url = reverse('course_report', args=[self.course_id])
        res = self.client.post(url)
        self.assertEqual(res.json()['status'], 'error')
        self.assertIn('no reason', res.json()['error'])

    def test_post_create_and_duplicate(self):
        url = reverse('course_report', args=[self.course_id])
        res1 = self.client.post(url, {'reason': 'r1'})
        self.assertEqual(res1.json()['status'], 'ok')
        rid = res1.json()['ok']
        res2 = self.client.post(url, {'reason': 'r2'})
        self.assertEqual(res2.json()['status'], 'error')
        self.assertIn('report already exists', res2.json()['error'])
