from django.shortcuts import render
import os
import markdown
def view_course(request,token):
    md_file_path = os.path.join('courses/', token+'.md')
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()
    html_content = markdown.markdown(md_content, extensions=['fenced_code', 'codehilite'])
    return render(request, 'course.html', {'content': html_content})


