from django.shortcuts import render, redirect
from .forms import CourseForm, LessonFormSet
from .models import Course, Lesson, Task

def home(request):
    return render(request, 'home.html')

def my_courses(request):
    courses = Course.objects.all()
    return render(request, 'my_courses.html', {'courses': courses})

def all_courses(request):
    # Здесь вы можете добавить логику для получения всех курсов
    return render(request, 'all_courses.html')

def add_course(request):
    if request.method == 'POST':
        course_form = CourseForm(request.POST)
        lesson_formset = LessonFormSet(request.POST)

        if course_form.is_valid() and lesson_formset.is_valid():
            course = course_form.save()
            lessons = lesson_formset.save(commit=False)
            for lesson in lessons:
                lesson.course = course
                lesson.save()
            return redirect('all_courses')  # Укажите URL для перенаправления

    else:
        course_form = CourseForm()
        lesson_formset = LessonFormSet(queryset=Lesson.objects.none())

    return render(request, 'add_courses.html', {
        'course_form': course_form,
        'lesson_formset': lesson_formset,
    })