from authentication.models import ResetRequest
from authentication.methods import user_info_view
from secrets import token_urlsafe

from django.test import TestCase, Client
from django.urls import reverse
from authentication.models import User
from django.contrib import messages
from home.models import UserProfile, SocialNetwork, Interest
from education.models import Courses, Stars


class RegisterViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')
        self.assertIn('RegisterForm', response.context)

    def test_register_view_post_success(self):
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
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_login_view_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertIn('LoginForm', response.context)

    def test_login_view_post_success(self):
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(reverse('login'), data, follow=True)
        self.assertTrue(response.context['user'].is_authenticated)

    def test_login_view_post_user_not_exist(self):
        data = {
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Такого пользователя не существует")

    def test_login_view_post_user_form_invalid(self):
        data = {
            'email': 'invalid',
            'password': ''
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Форма заполнена неправильно")


class LogoutViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_logout_view_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('logout'), follow=True)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertRedirects(response, '/')

    def test_logout_view_anonymous(self):
        response = self.client.get(reverse('logout'), follow=True)
        self.assertRedirects(response, '/login/')

class ResetPasswordViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_reset_password_view_get(self):
        response = self.client.get(reverse('reset_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'reset.html')
        self.assertIn('ResetPasswordForm', response.context)

    def test_reset_password_view_post_success(self):
        data = {'email': 'test@example.com'}
        response = self.client.post(reverse('reset_password'), data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ResetRequest.objects.filter(user=self.user).exists())

    def test_reset_password_view_post_user_not_exist(self):
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(reverse('reset_password'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пользователь с таким email не найден")

    def test_reset_password_view_post_form_invalid(self):
        data = {'email': 'invalid'}
        response = self.client.post(reverse('reset_password'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Форма заполнена неправильно")

    def test_reset_password_confirm_view_valid(self):
        token = token_urlsafe(32)

        # Создаем тестовый запрос для получения информации о клиенте
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
        response = self.client.get(
            reverse('reset_password_confirm', kwargs={'token': 'invalid'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Недействительная или устаревшая ссылка")


class ChangePasswordViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_change_password_view_get_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('change_password'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'change.html')
        self.assertIn('ChangePasswordForm', response.context)

    def test_change_password_view_get_anonymous(self):
        response = self.client.get(reverse('change_password'), follow=True)
        self.assertRedirects(response, '/login/')

    def test_change_password_view_post_success(self):
        self.client.login(email='test@example.com', password='testpass123')
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpass123'
        }
        response = self.client.post(reverse('change_password'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пароль успешно изменён")

    def test_change_password_view_post_wrong_old_password(self):
        self.client.login(email='test@example.com', password='testpass123')
        data = {
            'old_password': 'wrongpass',
            'new_password': 'newpass123'
        }
        response = self.client.post(reverse('change_password'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Старый пароль не совпадает")
