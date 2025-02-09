from django.shortcuts import render
import os
import markdown
from education.models import Courses, Lessons, Task


def view_course(request,token):
    lessons = os.listdir('courses/'+token)
    html_content=[]
    for i in lessons:
        with open('courses/'+token+'/' + i, 'r', encoding='utf-8') as f:
            md_content = f.read()
            html_content.append(markdown.markdown(md_content, extensions=['fenced_code', 'codehilite']))
    return render(request, 'course.html', {'content': html_content})


def all_courses(request):
    courses = Courses.objects.all()
    content = {
        'courses': []
    }
    for course in courses:
        course_info = {
            'id': course.course_id,
            'title': course.title
        }
        content['courses'].append(course_info)

    print(content['courses'])

    return render(request, 'all_courses.html', content)

