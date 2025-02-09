from django.shortcuts import render
import os
import markdown


def view_course(request,token):
    lessons = os.listdir('courses/'+token)
    html_content=[]
    for i in lessons:
        with open('courses/'+token+'/' + i, 'r', encoding='utf-8') as f:
            md_content = f.read()
            html_content.append(markdown.markdown(md_content, extensions=['fenced_code', 'codehilite']))
    return render(request, 'course.html', {'content': html_content})


