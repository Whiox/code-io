from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from home.models import UserProfile, SocialNetwork, Interest
from authentication.models import ResetRequest
from education.models import Topic, Courses, Lessons, Task, Stars

User = get_user_model()

# --- Инлайны для профиля ---
class SocialNetworkInline(admin.TabularInline):
    model = SocialNetwork
    extra = 0

class InterestInline(admin.TabularInline):
    model = Interest
    extra = 0

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0
    can_delete = False

# --- Пользователь ---
class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]
    list_display = ('email', 'username', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)

# Если `User` ещё не был зарегистрирован — регистрируем сразу,
# если же уже есть — перерегистрируем, перехватив исключение.
from django.contrib.admin.sites import AlreadyRegistered, NotRegistered

try:
    admin.site.unregister(User)
except NotRegistered:
    pass

admin.site.register(User, UserAdmin)


# --- Профиль пользователя ---
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'about', 'email', 'phone')
    inlines = [SocialNetworkInline, InterestInline]
    search_fields = ('user__username', 'email', 'phone')


# --- Соцсети ---
@admin.register(SocialNetwork)
class SocialNetworkAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'label', 'linc')
    search_fields = ('label', 'linc')


# --- Интересы ---
@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('user_profile', )
    search_fields = ('user_profile__user__username', )


# --- Курсы и вложенные уроки/задания ---
class LessonsInline(admin.TabularInline):
    model = Lessons
    extra = 0

@admin.register(Courses)
class CoursesAdmin(admin.ModelAdmin):
    list_display = ('title', 'author')
    search_fields = ('title', 'author__username')
    inlines = [LessonsInline]

class TaskInline(admin.TabularInline):
    model = Task
    extra = 0

@admin.register(Lessons)
class LessonsAdmin(admin.ModelAdmin):
    list_display = ('title', 'course')
    search_fields = ('title', 'course__title')
    inlines = [TaskInline]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('lesson', )
    search_fields = ('lesson__title', )


# --- Топики ---
@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', )
    search_fields = ('name', )


# --- Оценки ---
@admin.register(Stars)
class StarsAdmin(admin.ModelAdmin):
    list_display = ('course', 'user', 'data')
    search_fields = ('course__title', 'user__username')


# --- Запросы на сброс пароля ---
@admin.register(ResetRequest)
class ResetRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip', 'device', 'browser', 'os')
    search_fields = ('user__email', 'ip', 'device', 'browser', 'os')
