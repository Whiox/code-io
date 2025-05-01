from authentication.models import ResetRequest
from authentication.methods import user_info_view
from secrets import token_urlsafe

from django.test import TestCase, Client
from django.urls import reverse
from authentication.models import User
from django.contrib import messages
from home.models import UserProfile, SocialNetwork, Interest
from education.models import Courses, Stars


class AuthenticationViewsTests(TestCase):
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
            'password': 'short',
            'repeat_password': 'mismatch'
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Форма заполнена неправильно")
        
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
        
    def test_login_view_post_invalid(self):
        data = {
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Такого пользователя не существует")
        
    def test_logout_view_authenticated(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('logout'), follow=True)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertRedirects(response, '/')
        
    def test_logout_view_anonymous(self):
        response = self.client.get(reverse('logout'), follow=True)
        self.assertRedirects(response, '/login/')
        
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
        
    def test_reset_password_view_post_invalid(self):
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(reverse('reset_password'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Пользователь с таким email не найден")

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


class HomeViewsTests(TestCase):
    def setUp(self):
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
        self.interest = Interest.objects.create(
            user_profile=self.profile,
            label='Programming'
        )

    def test_home_view_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

        popular_courses = response.context['popular_courses']
        self.assertEqual(popular_courses[0].title, 'Course 1')
        self.assertEqual(popular_courses[0].stars_count, 2)

        self.assertTrue(hasattr(popular_courses[0], 'is_stared'))

    def test_home_view_anonymous(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

        popular_courses = response.context['popular_courses']
        self.assertEqual(popular_courses[0].title, 'Course 1')

        self.assertFalse(hasattr(popular_courses[0], 'is_stared'))

    def test_profile_view_get_owner(self):
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
        self.client.force_login(self.user2)
        response = self.client.get(reverse('profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['is_owner'], False)

    def test_profile_view_get_anonymous(self):
        response = self.client.get(reverse('profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 302)

    def test_profile_view_post_update_profile(self):
        self.client.force_login(self.user)
        data = {
            'username': 'newusername',
            'about': 'New about text',
            'email': 'new@example.com',
            'phone': '9876543210'
        }
        response = self.client.post(reverse('profile', args=[self.user.id]), data)
        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()
        self.profile.refresh_from_db()

        self.assertEqual(self.user.username, 'newusername')
        self.assertEqual(self.profile.about, 'New about text')
        self.assertEqual(self.profile.email, 'new@example.com')
        self.assertEqual(self.profile.phone, '9876543210')

    def test_profile_view_post_delete_account(self):
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
        self.client.force_login(self.user2)
        response = self.client.post(
            reverse('profile', args=[self.user.id]),
            {'username': 'hacked'}
        )

        messages_list = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(str(messages_list[0]), "У вас нет прав на изменение этого профиля.")

        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'testuser')

class AuthenticationEndpointsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_data = {
            'username': 'tester',
            'password': 'secret123',
            'email': 't@test.com',
        }
        User.objects.create_user(**self.user_data)

    def test_login_endpoint(self):
        url = reverse('login')
        resp = self.client.post(url, {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
        })
        self.assertEqual(resp.status_code, 200)

    def test_register_endpoint(self):
        url = reverse('register')
        resp = self.client.post(url, {
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'email': 'new@u.com',
        })
        self.assertIn(resp.status_code, (200, 302))

class EducationEndpointsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='edu',
            email='edu@test.com',
            password='edu123'
        )
        self.client.login(username='edu', password='edu123')

    def test_course_list_endpoint(self):
        url = reverse('all')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_course_detail_endpoint(self):
        course = Courses.objects.create(title='Test', author=self.user)
        url = reverse('course', args=[course.course_id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
