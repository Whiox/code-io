"""
admin.py

Модуль админки Django для управления:
- Пользователями и их профилями
- Социальными сетями и интересами
- Курсами, уроками и заданиями
- Темами курсов
- Звёздочками (оценками) курсов
- Запросами на сброс пароля

Здесь регистрируются все модели и определяются inline‐классы для удобного редактирования связанных сущностей.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.sites import NotRegistered

from home.models import UserProfile, SocialNetwork, Technology
from authentication.models import ResetRequest
from education.models import Topic, Courses, Lessons, Task, Stars

User = get_user_model()


# --- Инлайны для профиля ---
class SocialNetworkInline(admin.TabularInline):
    """
    Inline-класс для отображения и редактирования
    объектов SocialNetwork в интерфейсе профиля пользователя.
    """
    model = SocialNetwork
    extra = 0


class InterestInline(admin.TabularInline):
    """
    Inline-класс для отображения и редактирования
    объектов Interest (интересов) в интерфейсе профиля пользователя.
    """
    model = Technology
    extra = 0


class UserProfileInline(admin.StackedInline):
    """
    Inline-класс для редактирования основных полей UserProfile
    прямо на странице редактирования пользователя в админке.
    """
    model = UserProfile
    extra = 0
    can_delete = False


# --- Пользователь ---
class UserAdmin(BaseUserAdmin):
    """
    Расширение стандартной админки для модели User.
    Добавляет inline-редактирование профиля и настраивает
    отображаемые и ищущиеся поля.
    """
    inlines = [UserProfileInline]
    list_display = ('email', 'username', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)


# Если `User` ещё не был зарегистрирован — регистрируем сразу,
# если же уже есть — перерегистрируем, перехватив исключение.
try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, UserAdmin)


# --- Профиль пользователя ---
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Админка для модели UserProfile.
    Отображает пользователя, контактную информацию и описание,
    а также inline-редактирование социальных сетей и интересов.
    """
    list_display = ('user', 'about', 'email')
    inlines = [SocialNetworkInline, InterestInline]
    search_fields = ('user__username', 'email')


# --- Соцсети ---
@admin.register(SocialNetwork)
class SocialNetworkAdmin(admin.ModelAdmin):
    """
    Админка для модели SocialNetwork.
    Позволяет управлять записями социальных сетей,
    привязанных к профилю пользователя.
    """
    list_display = ('user_profile', 'label', 'linc')
    search_fields = ('label', 'linc')


# --- Интересы ---
@admin.register(Technology)
class InterestAdmin(admin.ModelAdmin):
    """
    Админка для модели Interest.
    Позволяет управлять списком интересов пользователя.
    """
    list_display = ('user_profile',)
    search_fields = ('user_profile__user__username',)


# --- Курсы и вложенные уроки/задания ---
class LessonsInline(admin.TabularInline):
    """
    Inline-класс для отображения уроков (Lessons)
    на странице редактирования курса.
    """
    model = Lessons
    extra = 0


@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    """
    Админка для модели Courses.
    Отображает название и автора курса,
    а также позволяет редактировать уроки inline.
    """
    list_display = ('title', 'author')
    search_fields = ('title', 'author__username')
    inlines = [LessonsInline]


class TaskInline(admin.TabularInline):
    """
    Inline-класс для отображения задач (Task)
    на странице редактирования урока.
    """
    model = Task
    extra = 0


@admin.register(Lessons)
class LessonsAdmin(admin.ModelAdmin):
    """
    Админка для модели Lessons.
    Отображает название урока и связанный курс,
    а также позволяет редактировать задачи inline.
    """
    list_display = ('title', 'course')
    search_fields = ('title', 'course__title')
    inlines = [TaskInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Админка для модели Task.
    Отображает задачи, связанные с уроком.
    """
    list_display = ('lesson',)
    search_fields = ('lesson__title',)


# --- Топики ---
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """
    Админка для модели Topic.
    Позволяет управлять темами курсов.
    """
    list_display = ('name',)
    search_fields = ('name',)


# --- Оценки ---
@admin.register(Stars)
class StarsAdmin(admin.ModelAdmin):
    """
    Админка для модели Stars.
    Отображает оценки пользователей для курсов.
    """
    list_display = ('course', 'user', 'data')
    search_fields = ('course__title', 'user__username')


# --- Запросы на сброс пароля ---
@admin.register(ResetRequest)
class ResetRequestAdmin(admin.ModelAdmin):
    """
    Админка для модели ResetRequest.
    Отображает запросы на сброс пароля с метаданными о браузере и устройстве.
    """
    list_display = ('user', 'ip', 'device', 'browser', 'os')
    search_fields = ('user__email', 'ip', 'device', 'browser', 'os')
