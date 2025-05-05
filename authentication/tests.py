"""Тесты для authentication/views. """

from authentication.models import ResetRequest
from authentication.methods import user_info_view
from secrets import token_urlsafe

from django.test import TestCase, Client
from django.urls import reverse
from authentication.models import User


class RegisterViewsTests(TestCase):
    """Тесты для функционала регистрации пользователей"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_register_view_get(self):
        """Тест GET-запроса страницы регистрации"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIn('RegisterForm', response.context)

    def test_register_view_post_success(self):
        """Тест успешной регистрации нового пользователя"""
        data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'repeat_password': 'newpass123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_register_view_post_invalid(self):
        """Тест регистрации с невалидными данными"""
        data = {
            'email': 'invalid',
            'username': '',
            'password': 'newpass123',
            'repeat_password': 'newpass123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Форма заполнена неправильно")

    def test_register_view_password_not_match(self):
        """Тест несовпадения паролей при регистрации"""
        data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'pass1',
            'repeat_password': 'pass2'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пароли не совпадают")

    def test_register_view_users_already_exist(self):
        """Тест регистрации с существующей почтой"""
        data = {
            'email': 'test@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'repeat_password': 'newpass123'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пользователь с такой почтой уже зарегистрирован.")


class LoginViewsTest(TestCase):
    """Тесты для функционала авторизации пользователей"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_login_view_get(self):
        """Тест GET-запроса страницы авторизации"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIn('LoginForm', response.context)

    def test_login_view_post_success(self):
        """Тест успешной авторизации"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('login'), data, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_view_post_user_not_exist(self):
        """Тест авторизации несуществующего пользователя"""
        data = {
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Такого пользователя не существует")

    def test_login_view_post_user_form_invalid(self):
        """Тест авторизации с невалидной формой"""
        data = {
            'email': 'invalid',
            'password': ''
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Форма заполнена неправильно")


class LogoutViewsTest(TestCase):
    """Тесты для функционала выхода из системы"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_logout_view_authenticated(self):
        """Тест выхода для авторизованного пользователя"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('logout'), follow=True)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertRedirects(response, '/')

    def test_logout_view_anonymous(self):
        """Тест выхода для анонимного пользователя"""
        response = self.client.get(reverse('logout'), follow=True)
        self.assertRedirects(response, '/login/')


class ResetPasswordViewsTest(TestCase):
    """Тесты для функционала сброса пароля"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_reset_password_view_get(self):
        """Тест GET-запроса страницы сброса пароля"""
        response = self.client.get(reverse('reset_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reset.html')
        self.assertIn('ResetPasswordForm', response.context)

    def test_reset_password_view_post_success(self):
        """Тест успешного запроса на сброс пароля"""
        data = {'email': 'test@example.com'}
        response = self.client.post(reverse('reset_password'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ResetRequest.objects.filter(user=self.user).exists())

    def test_reset_password_view_post_user_not_exist(self):
        """Тест запроса сброса для несуществующего email"""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(reverse('reset_password'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пользователь с таким email не найден")

    def test_reset_password_view_post_form_invalid(self):
        """Тест сброса пароля с невалидной формой"""
        data = {'email': 'invalid'}
        response = self.client.post(reverse('reset_password'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Форма заполнена неправильно")

    def test_reset_password_confirm_view_valid(self):
        """Тест подтверждения сброса с валидным токеном"""
        token = token_urlsafe(32)

        # Получение информации о клиенте для создания ResetRequest
        request = self.client.get('/').wsgi_request
        info = user_info_view(request)

        ResetRequest.objects.create(
            user=self.user,
            url=token,
            **info
        )
        response = self.client.get(
            reverse('reset_password_confirm', kwargs={'token': token})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Новый пароль отправлен вам на почту")

    def test_reset_password_confirm_view_invalid(self):
        """Тест подтверждения сброса с невалидным токеном"""
        response = self.client.get(
            reverse('reset_password_confirm', kwargs={'token': 'invalid'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Недействительная или устаревшая ссылка")


class ChangePasswordViewsTest(TestCase):
    """Тесты для функционала изменения пароля"""

    def setUp(self):
        """Инициализация тестовых данных"""
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_change_password_view_get_authenticated(self):
        """Тест доступа к форме смены пароля для авторизованного"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('change_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change.html')
        self.assertIn('ChangePasswordForm', response.context)

    def test_change_password_view_get_anonymous(self):
        """Тест доступа к форме смены пароля для анонима"""
        response = self.client.get(reverse('change_password'), follow=True)
        self.assertRedirects(response, '/login/')

    def test_change_password_view_post_success(self):
        """Тест успешной смены пароля"""
        self.client.login(email='test@example.com', password='testpass123')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123'
        }
        response = self.client.post(reverse('change_password'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пароль успешно изменён")

    def test_change_password_view_post_wrong_old_password(self):
        """Тест смены пароля с неверным старым паролем"""
        self.client.login(email='test@example.com', password='testpass123')
        data = {
            'old_password': 'wrongpass',
            'new_password': 'newpass123'
        }
        response = self.client.post(reverse('change_password'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Старый пароль не совпадает")
