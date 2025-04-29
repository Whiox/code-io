from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin.sites import NotRegistered

from home.models import UserProfile, SocialNetwork, Interest
from authentication.models import ResetRequest
from education.models import Topic, Courses, Lessons, Task, Stars

User = get_user_model()


class SocialNetworkInline(admin.TabularInline):
    """
    Inline-класс для редактирования социальных сетей пользователя.

    :ivar model: модель SocialNetwork
    :vartype model: django.db.models.Model
    :ivar int extra: количество дополнительных пустых форм для создания записей
    """
    model = SocialNetwork
    extra = 0


class InterestInline(admin.TabularInline):
    """
    Inline-класс для редактирования интересов пользователя.

    :ivar model: модель Interest
    :vartype model: django.db.models.Model
    :ivar int extra: количество дополнительных пустых форм для создания записей
    """
    model = Interest
    extra = 0


class UserProfileInline(admin.StackedInline):
    """
    Inline-класс для редактирования профиля пользователя на странице User.

    :ivar model: модель UserProfile
    :vartype model: django.db.models.Model
    :ivar int extra: количество дополнительных пустых форм
    :ivar bool can_delete: возможность удаления профиля из админки User
    """
    model = UserProfile
    extra = 0
    can_delete = False


class UserAdmin(BaseUserAdmin):
    """
    Админка для кастомной модели User.

    Добавляет возможность редактирования связанных профилей и настраивает
    поля для отображения, поиска и сортировки.

    :ivar list inlines: список Inline-классов для отображения на странице User
    :vartype inlines: list
    :ivar tuple list_display: поля, отображаемые в списке пользователей
    :ivar tuple search_fields: поля для поиска пользователей в админке
    :ivar tuple ordering: поля для сортировки списка пользователей
    """
    inlines = [UserProfileInline]
    list_display = ('email', 'username', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)


try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Админка для модели UserProfile.

    Отображает основную информацию профиля и предоставляет
    inline-редактирование социальных сетей и интересов.

    :ivar tuple list_display: поля, отображаемые в списке профилей
    :ivar list inlines: Inline-классы для редактирования связанных моделей
    :ivar tuple search_fields: поля для поиска профилей
    """
    list_display = ('user', 'about', 'email', 'phone')
    inlines = [SocialNetworkInline, InterestInline]
    search_fields = ('user__username', 'email', 'phone')


@admin.register(SocialNetwork)
class SocialNetworkAdmin(admin.ModelAdmin):
    """
    Админка для модели SocialNetwork.

    Позволяет управлять связями социальных сетей с профилем пользователя.

    :ivar tuple list_display: поля, отображаемые в списке соцсетей
    :ivar tuple search_fields: поля для поиска записей социальных сетей
    """
    list_display = ('user_profile', 'label', 'linc')
    search_fields = ('label', 'linc')


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    """
    Админка для модели Interest.

    Позволяет управлять списком интересов пользователя.

    :ivar tuple list_display: поля, отображаемые в списке интересов
    :ivar tuple search_fields: поля для поиска интересов по имени профиля пользователя
    """
    list_display = ('user_profile',)
    search_fields = ('user_profile__user__username',)


class LessonsInline(admin.TabularInline):
    """
    Inline-класс для отображения уроков в админке курсов.

    :ivar model: модель Lessons
    :vartype model: django.db.models.Model
    :ivar int extra: количество дополнительных пустых форм для создания уроков
    """
    model = Lessons
    extra = 0


@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    """
    Админка для модели Courses.

    Позволяет управлять курсами и их уроками через inline.

    :ivar tuple list_display: поля, отображаемые в списке курсов
    :ivar tuple search_fields: поля для поиска курсов
    :ivar list inlines: Inline-класс для редактирования уроков курса
    """
    list_display = ('title', 'author')
    search_fields = ('title', 'author__username')
    inlines = [LessonsInline]


class TaskInline(admin.TabularInline):
    """
    Inline-класс для отображения заданий в админке уроков.

    :ivar model: модель Task
    :vartype model: django.db.models.Model
    :ivar int extra: количество дополнительных пустых форм для создания заданий
    """
    model = Task
    extra = 0


@admin.register(Lessons)
class LessonsAdmin(admin.ModelAdmin):
    """
    Админка для модели Lessons.

    Позволяет управлять уроками и их заданиями через inline.

    :ivar tuple list_display: поля, отображаемые в списке уроков
    :ivar tuple search_fields: поля для поиска уроков
    :ivar list inlines: Inline-класс для редактирования заданий урока
    """
    list_display = ('title', 'course')
    search_fields = ('title', 'course__title')
    inlines = [TaskInline]


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Админка для модели Task.

    Позволяет управлять заданиями уроков.

    :ivar tuple list_display: поля, отображаемые в списке заданий
    :ivar tuple search_fields: поля для поиска заданий по названию урока
    """
    list_display = ('lesson',)
    search_fields = ('lesson__title',)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    """
    Админка для модели Topic.

    Позволяет управлять темами курсов.

    :ivar tuple list_display: поля, отображаемые в списке тем
    :ivar tuple search_fields: поля для поиска тем по названию
    """
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Stars)
class StarsAdmin(admin.ModelAdmin):
    """
    Админка для модели Stars.

    Позволяет управлять оценками пользователей для курсов.

    :ivar tuple list_display: поля, отображаемые в списке оценок
    :ivar tuple search_fields: поля для поиска оценок по курсу и пользователю
    """
    list_display = ('course', 'user', 'data')
    search_fields = ('course__title', 'user__username')


@admin.register(ResetRequest)
class ResetRequestAdmin(admin.ModelAdmin):
    """
    Админка для модели ResetRequest.

    Отображает запросы на сброс пароля вместе с метаданными об окружении отправителя.

    :ivar tuple list_display: поля, отображаемые в списке запросов
    :ivar tuple search_fields: поля для поиска запросов по пользователю, IP и устройству
    """
    list_display = ('user', 'ip', 'device', 'browser', 'os')
    search_fields = ('user__email', 'ip', 'device', 'browser', 'os')
