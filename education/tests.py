"""Тесты для education/views. """

import os
import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls import reverse

from authentication.models import User
from education.models import Courses, Stars


class AllCourseViewTest(TestCase):
    """Тесты для представления списка всех курсов"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_all_course_get(self):
        """Тест GET-запроса для страницы всех курсов"""
        response = self.client.get(reverse('all'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'all_courses.html')


class StaredCoursesViewTest(TestCase):
    """Тесты для представления избранных курсов"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_stared_view_get_authenticated(self):
        """Тест доступа авторизованного пользователя к избранным курсам"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('stared'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stared_courses.html')

    def test_stared_view_get_anonymous(self):
        """Тест перенаправления анонимного пользователя со страницы избранного"""
        response = self.client.get(reverse('stared'))
        self.assertEqual(response.status_code, 302)


class MyCoursesViewTest(TestCase):
    """Тесты для представления личных курсов пользователя"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_my_view_get_authenticated(self):
        """Тест доступа авторизованного пользователя к своим курсам"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('my_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_courses.html')

    def test_my_view_get_anonymous(self):
        """Тест перенаправления анонимного пользователя со страницы личных курсов"""
        response = self.client.get(reverse('my_courses'))
        self.assertEqual(response.status_code, 302)


class CreateCourseViewTest(TestCase):
    """Тесты для представления создания курса"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_create_view_get_authenticated(self):
        """Тест доступа авторизованного пользователя к форме создания курса"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('add_course'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_course.html')

    def test_create_view_get_anonymous(self):
        """Тест перенаправления анонимного пользователя со страницы создания курса"""
        response = self.client.get(reverse('add_course'))
        self.assertEqual(response.status_code, 302)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ViewCourseViewTest(TestCase):
    """Тесты для представления просмотра курса с временной медиа-директорией"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = Client()
        self.user = User.objects.create_user(email='u@e.com', username='u', password='p')
        self.course = Courses.objects.create(title='Test', author=self.user)
        self.course_id = self.course.course_id

    def tearDown(self):
        """Очистка временной медиа-директории"""
        shutil.rmtree(self._get_media_root(), ignore_errors=True)

    def _get_media_root(self):
        """Получение пути к временной медиа-директории"""
        return os.environ.get('DJANGO_TEST_TEMP_MEDIA_ROOT') or tempfile.gettempdir()

    def test_get_nonexistent_dir(self):
        """Тест обработки несуществующего курса"""
        url = reverse('course', args=[self.course_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'error.html')
        self.assertIn('Курс не найден.', response.context['error'])


class DeleteCourseViewTest(TestCase):
    """Тесты для представления удаления курса"""

    def setUp(self):
        """Инициализация тестовых данных и временной медиа-директории"""
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
        """Очистка временных настроек и медиа-директории"""
        self.patch.disable()
        shutil.rmtree(self.media, ignore_errors=True)

    def test_get_not_author(self):
        """Тест попытки удаления курса не автором"""
        self.client.login(email='o@e.com', password='p')
        url = reverse('delete', args=[self.course_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'error.html')

    def test_get_author(self):
        """Тест доступа автора к странице подтверждения удаления"""
        self.client.login(email='u@e.com', password='p')
        url = reverse('delete', args=[self.course_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'confirm_delete.html')

    def test_post_not_author(self):
        """Тест POST-запроса на удаление от не автора"""
        self.client.login(email='o@e.com', password='p')
        url = reverse('delete', args=[self.course_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'error.html')

    def test_post_author(self):
        """Тест успешного удаления курса автором"""
        self.client.login(email='u@e.com', password='p')
        url = reverse('delete', args=[self.course_id])
        response = self.client.post(url, follow=True)
        self.assertRedirects(response, reverse('my_courses'))
        self.assertFalse(Courses.objects.filter(course_id=self.course_id).exists())
        self.assertFalse(os.path.exists(os.path.join(self.media, str(self.course_id))))


class AddStarViewTest(TestCase):
    """Тесты для добавления/удаления звезд курсам"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = Client()
        self.user = User.objects.create_user(email='u@e.com', username='u', password='p')
        self.course = Courses.objects.create(title='Star', author=self.user)
        self.course_id = self.course.course_id

    def test_post_anonymous(self):
        """Тест добавления звезды анонимным пользователем"""
        url = reverse('add_star', args=[self.course_id])
        response = self.client.post(url)
        self.assertEqual(response.json()['status'], False)

    def test_post_toggle(self):
        """Тест переключения состояния звезды (добавление/удаление)"""
        self.client.login(email='u@e.com', password='p')
        url = reverse('add_star', args=[self.course_id])
        res1 = self.client.post(url)
        self.assertTrue(res1.json()['status'])
        self.assertTrue(Stars.objects.filter(user=self.user, course=self.course).exists())
        res2 = self.client.post(url)
        self.assertFalse(res2.json()['status'])
        self.assertFalse(Stars.objects.filter(user=self.user, course=self.course).exists())


class ReportCourseViewTest(TestCase):
    """Тесты для системы жалоб на курсы"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = Client()
        self.user = User.objects.create_user(email='u@e.com', username='u', password='p')
        self.course = Courses.objects.create(title='Rpt', author=self.user)
        self.course_id = self.course.course_id
        self.client.login(email='u@e.com', password='p')

    def test_get(self):
        """Тест доступа к форме отправки жалобы"""
        url = reverse('course_report', args=[self.course_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'report_course.html')
        self.assertIn('course', response.context)

    def test_post_no_reason(self):
        """Тест отправки жалобы без указания причины"""
        url = reverse('course_report', args=[self.course_id])
        res = self.client.post(url)
        self.assertEqual(res.json()['status'], 'error')
        self.assertIn('no reason', res.json()['error'])

    def test_post_create_and_duplicate(self):
        """Тест создания жалобы и проверки на дубликаты"""
        url = reverse('course_report', args=[self.course_id])
        res1 = self.client.post(url, {'reason': 'r1'})
        self.assertEqual(res1.json()['status'], 'ok')
        rid = res1.json()['ok']
        res2 = self.client.post(url, {'reason': 'r2'})
        self.assertEqual(res2.json()['status'], 'error')
        self.assertIn('report already exists', res2.json()['error'])
