import os
import shutil
import tempfile
from django.forms import formset_factory
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from authentication.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http import QueryDict
from django.conf import settings
from education.models import Courses, Lessons, Stars, ReportCourse, Topic, CourseProgress
from education.forms import AddCourseForm, AddLessonForm

TEST_MEDIA_ROOT = tempfile.mkdtemp()


class AllCoursesViewTest(TestCase):
    """Тесты для представления списка всех курсов"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.course = Courses.objects.create(title='Test Course', author=self.user)
        self.topic = Topic.objects.create(name='Programming', author=self.user)
        self.course.topics.add(self.topic)

    def test_all_courses_view_returns_200(self):
        response = self.client.get(reverse('all'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'all_courses.html')

    def test_course_list_in_context(self):
        response = self.client.get(reverse('all'))
        self.assertIn('courses', response.context)
        self.assertEqual(len(response.context['courses']), 1)

    def test_star_flag_for_authenticated_user(self):
        Stars.objects.create(user=self.user, course=self.course)
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('all'))
        self.assertTrue(response.context['courses'][0]['is_stared'])


class StaredCoursesViewTest(TestCase):
    """Тесты для представления избранных курсов"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.course = Courses.objects.create(title='Test Course', author=self.user)
        Stars.objects.create(user=self.user, course=self.course)

    def test_authenticated_access(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('stared'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'stared_courses.html')

    def test_stared_courses_in_context(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('stared'))
        self.assertEqual(len(response.context['courses']), 1)
        self.assertEqual(response.context['courses'][0]['title'], 'Test Course')

    def test_popular_courses_fallback(self):
        Stars.objects.all().delete()
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('stared'))
        self.assertIsNotNone(response.context['popular_courses'])


class MyCoursesViewTest(TestCase):
    """Тесты для представления личных курсов пользователя"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.course = Courses.objects.create(title='My Course', author=self.user)

    def test_authenticated_access(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('my_courses'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'my_courses.html')

    def test_user_courses_in_context(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('my_courses'))
        self.assertEqual(len(response.context['courses']), 1)
        self.assertEqual(response.context['courses'][0]['title'], 'My Course')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class AddCourseViewTest(TestCase):
    """Тесты для представления создания курса"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client.login(email='test@example.com', password='testpass123')

    def test_successful_creation(self):
        lesson_file = SimpleUploadedFile('test.md', b'Test content')
        data = {
            'course_name': 'New Course',
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-0-lesson_description': 'First lesson',
            'form-0-lesson_file': lesson_file,
        }
        response = self.client.post(reverse('add_course'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Courses.objects.filter(title='New Course').exists())

    def test_invalid_form_submission(self):
        data = {
            'course_name': '',
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '0',
            'form-0-lesson_description': '',
        }
        response = self.client.post(reverse('add_course'), data)
        self.assertTrue(response.context['course_form'].errors)

    def tearDown(self):
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ViewCourseViewTest(TestCase):
    """Тесты для представления просмотра курса"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.course = Courses.objects.create(title='Test Course', author=self.user)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, str(self.course.course_id)), exist_ok=True)

    def test_course_display(self):
        Lessons.objects.create(course=self.course, title='Lesson 1', order=0)
        response = self.client.get(reverse('course', args=[self.course.course_id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('lessons', response.context)

    def test_missing_course_directory(self):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, str(self.course.course_id)))
        response = self.client.get(reverse('course', args=[self.course.course_id]))
        self.assertTemplateUsed(response, 'error.html')

    def tearDown(self):
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class DeleteCourseViewTest(TestCase):
    """Тесты для представления удаления курса"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.other_user = User.objects.create_user(
            email='other@example.com',
            username='otheruser',
            password='testpass123'
        )
        self.course = Courses.objects.create(title='Test Course', author=self.user)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, str(self.course.course_id)), exist_ok=True)

    def test_author_access(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('delete', args=[self.course.course_id]))
        self.assertTemplateUsed(response, 'confirm_delete.html')

    def test_non_author_access(self):
        self.client.login(email='other@example.com', password='testpass123')
        response = self.client.get(reverse('delete', args=[self.course.course_id]))
        self.assertTemplateUsed(response, 'error.html')

    def test_successful_deletion(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.post(reverse('delete', args=[self.course.course_id]))
        self.assertFalse(Courses.objects.filter(pk=self.course.pk).exists())

    def tearDown(self):
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)


class AddStarViewTest(TestCase):
    """Тесты для добавления/удаления звезд"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.course = Courses.objects.create(title='Test Course', author=self.user)

    def test_star_toggle(self):
        self.client.login(email='test@example.com', password='testpass123')

        # Добавление звезды
        response = self.client.post(reverse('add_star', args=[self.course.course_id]))
        self.assertTrue(response.json()['status'])
        self.assertTrue(Stars.objects.filter(user=self.user, course=self.course).exists())

        # Удаление звезды
        response = self.client.post(reverse('add_star', args=[self.course.course_id]))
        self.assertFalse(response.json()['status'])
        self.assertFalse(Stars.objects.filter(user=self.user, course=self.course).exists())

    def test_anonymous_user(self):
        response = self.client.post(reverse('add_star', args=[self.course.course_id]))
        self.assertEqual(response.json()['status'], False)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class ReportCourseViewTest(TestCase):
    """Тесты для системы жалоб на курсы"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.course = Courses.objects.create(title='Test Course', author=self.user)
        self.client.login(email='test@example.com', password='testpass123')

    def test_duplicate_report(self):
        self.client.post(
            reverse('course_report', args=[self.course.course_id]),
            {'reason': 'First report'}
        )
        response = self.client.post(
            reverse('course_report', args=[self.course.course_id]),
            {'reason': 'Duplicate report'}
        )
        self.assertEqual(response.json()['status'], 'error')


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class CourseEditorViewTest(TestCase):
    """Тесты для редактора курсов"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.course = Courses.objects.create(title='Test Course', author=self.user)
        os.makedirs(os.path.join(settings.MEDIA_ROOT, str(self.course.course_id)), exist_ok=True)

    def test_editor_access(self):
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('course_edit', args=[self.course.course_id]))
        self.assertTemplateUsed(response, 'edit_course.html')

    def test_lesson_content_update(self):
        self.client.login(email='test@example.com', password='testpass123')
        file_path = os.path.join(settings.MEDIA_ROOT, str(self.course.course_id), 'lesson_0.md')

        with open(file_path, 'w') as f:
            f.write('Old content')

        response = self.client.post(
            reverse('course_edit', args=[self.course.course_id]),
            {'lesson': '0', 'content': 'New content'}
        )

        with open(file_path, 'r') as f:
            self.assertEqual(f.read(), 'New content')

    def tearDown(self):
        if os.path.exists(TEST_MEDIA_ROOT):
            shutil.rmtree(TEST_MEDIA_ROOT)


class ProgressTrackingTest(TestCase):
    """Тесты для отслеживания прогресса"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.course = Courses.objects.create(title='Test Course', author=self.user)
        self.lesson = Lessons.objects.create(course=self.course, title='Lesson 1')

    def test_progress_toggle(self):
        self.client.login(email='test@example.com', password='testpass123')

        response = self.client.post(
            reverse('lesson_progress', args=[self.course.course_id, self.lesson.pk])
        )
        self.assertTrue(CourseProgress.objects.exists())

        response = self.client.post(
            reverse('lesson_progress', args=[self.course.course_id, self.lesson.pk])
        )
        self.assertFalse(CourseProgress.objects.first().status)


class TopicManagementTest(TestCase):
    """Тесты для управления темами"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        self.client.login(email='test@example.com', password='testpass123')

    def test_topic_creation(self):
        response = self.client.post(
            reverse('create_topic'),
            {'name': 'New Topic'}
        )
        self.assertEqual(response.json()['status'], 'ok')

    def test_duplicate_topic_prevention(self):
        Topic.objects.create(name='Existing Topic', author=self.user)
        response = self.client.post(
            reverse('create_topic'),
            {'name': 'Existing Topic'}
        )
        self.assertEqual(response.json()['status'], 'error')
