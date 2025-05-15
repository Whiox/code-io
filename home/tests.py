"""Тесты для home.views. """

from django.test import TestCase, Client
from django.urls import reverse
from authentication.models import User
from django.contrib import messages
from home.models import UserProfile, SocialNetwork, Technology
from education.models import Courses, Stars


class HomeViewsTests(TestCase):
    """Тесты для проверки views приложения home"""

    def setUp(self):
        """Настройка тестовых данных перед выполнением каждого теста"""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            username='testuser'
        )
        self.user2 = User.objects.create_user(
            email='test2@example.com',
            password='testpass123',
            username='testuser2'
        )

        self.course1 = Courses.objects.create(title='Course 1', author=self.user)
        self.course2 = Courses.objects.create(title='Course 2', author=self.user)
        self.course3 = Courses.objects.create(title='Course 3', author=self.user)
        Stars.objects.create(course=self.course1, user=self.user)
        Stars.objects.create(course=self.course1, user=self.user2)
        Stars.objects.create(course=self.course2, user=self.user)

        self.profile = UserProfile.objects.create(
            user=self.user,
            about='Test about',
            email='profile@example.com',
            phone='1234567890'
        )
        self.social = SocialNetwork.objects.create(
            user_profile=self.profile,
            label='GitHub',
            linc='https://github.com/test'
        )
        self.interest = Technology.objects.create(
            user_profile=self.profile,
            label='Programming'
        )

    def test_home_view_authenticated(self):
        """Тест главной страницы для аутентифицированного пользователя"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

        popular_courses = response.context['popular_courses']
        self.assertEqual(popular_courses[0].title, 'Course 1')
        self.assertEqual(popular_courses[0].stars_count, 2)
        self.assertTrue(hasattr(popular_courses[0], 'is_stared'))

    def test_home_view_anonymous(self):
        """Тест главной страницы для анонимного пользователя"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

        popular_courses = response.context['popular_courses']
        self.assertEqual(popular_courses[0].title, 'Course 1')
        self.assertFalse(hasattr(popular_courses[0], 'is_stared'))

    def test_profile_view_get_owner(self):
        """Тест просмотра профиля владельцем"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile', args=[self.user.id]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')

        context = response.context
        self.assertEqual(context['username'], 'testuser')
        self.assertEqual(context['user_profile'].about, 'Test about')
        self.assertEqual(context['is_owner'], True)
        self.assertEqual(len(context['social_network']), 1)
        self.assertEqual(len(context['interest']), 1)

    def test_profile_view_get_not_owner(self):
        """Тест просмотра профиля другим пользователем"""
        self.client.force_login(self.user2)
        response = self.client.get(reverse('profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['is_owner'], False)

    def test_profile_view_get_anonymous(self):
        """Тест просмотра профиля анонимным пользователем"""
        response = self.client.get(reverse('profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_post_update_profile(self):
        """Тест обновления данных профиля"""
        self.client.force_login(self.user)
        data = {
            'username': 'newusername',
            'about': 'New about text',
            'email': 'new@example.com',
            'phone': '9876543210'
        }
        response = self.client.post(reverse('profile', args=[self.user.id]), data)
        self.assertEqual(response.status_code, 302)

        # Проверка обновленных данных
        self.user.refresh_from_db()
        self.profile.refresh_from_db()
        self.assertEqual(self.user.username, 'newusername')
        self.assertEqual(self.profile.about, 'New about text')
        self.assertEqual(self.profile.email, 'new@example.com')
        self.assertEqual(self.profile.phone, '9876543210')

    def test_profile_view_post_delete_account(self):
        """Тест удаления аккаунта"""
        self.client.force_login(self.user)
        user_id = self.user.id
        response = self.client.post(
            reverse('profile', args=[user_id]),
            {'action': 'delete_account'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        self.assertFalse(User.objects.filter(id=user_id).exists())

    def test_profile_view_post_not_owner(self):
        """Тест попытки изменения чужого профиля"""
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse('profile', args=[self.user.id]),
            {'username': 'hacked'}
        )
        # Проверка сообщения об ошибке
        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), "У вас нет прав на изменение этого профиля.")
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'testuser')


class AuthenticationEndpointsTest(TestCase):
    """Тесты endpoints аутентификации"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        self.user_data = {
            'username': 'tester',
            'password': 'secret123',
            'email': 't@test.com',
        }
        User.objects.create_user(**self.user_data)

    def test_login_endpoint(self):
        """Тест авторизации пользователя"""
        url = reverse('login')
        resp = self.client.post(url, {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
        })
        self.assertEqual(resp.status_code, 200)

    def test_register_endpoint(self):
        """Тест регистрации нового пользователя"""
        url = reverse('register')
        resp = self.client.post(url, {
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'email': 'new@u.com',
        })
        self.assertIn(resp.status_code, (200, 302))


class EducationEndpointsTest(TestCase):
    """Тесты endpoints приложения education"""

    def setUp(self):
        """Настройка тестовых данных"""
        self.client = Client()
        self.user = User.objects.create_user(
            username='edu',
            email='edu@test.com',
            password='edu123'
        )
        self.client.login(username='edu', password='edu123')

    def test_course_list_endpoint(self):
        """Тест получения списка курсов"""
        url = reverse('all')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_course_detail_endpoint(self):
        """Тест получения детальной информации о курсе"""
        course = Courses.objects.create(title='Test', author=self.user)
        url = reverse('course', args=[course.course_id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
