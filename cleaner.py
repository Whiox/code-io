import sqlite3
import os
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

cursor.execute("SELECT course_id FROM education_courses")
bd = [str(i[0]) for i in cursor.fetchall()]
bd.sort(key=lambda x: int(x))
lessons = dict()
for i in bd:
    lessons[i] = []
cursor.execute("SELECT lesson_id, course_id FROM education_lessons")
for i in cursor.fetchall():
    lessons[str(i[1])].append(str(i[0]))
    lessons[str(i[1])].sort(key= lambda x: int(x))
print()
conn.close()
os.chdir("courses")
data = sorted(os.listdir(), key=lambda x: int(x))
f = True
for i in bd:
    if i not in data:
        f = False
        print(f"Курса {i} нет в файловой системе")
        for j in lessons[i]:
            print(f"    урока {j} нет в файловой системе")
    else:
        print(f"Курс {i} есть в файловой системе")
        os.chdir(i)
        d = sorted(os.listdir())
        for j in lessons[i]:
            if (j + ".md") not in d:
                print(f"    Урока {j} нет в файловой системе")
        os.chdir("..")
for i in data:
    if i not in bd:
        print(f"Курса {i} нет в БД")
        os.chdir(i)
        d = sorted(os.listdir())
        for j in d:
            print(f"    Урока {j} нет в файловой системе")
        os.chdir("..")
    else:
        print(f"Курс {i} есть в БД")
        os.chdir(i)
        d = sorted(os.listdir())
        for j in d:
            if os.path.isfile(j):
                x = j.replace('.md', '')
                if x not in lessons[i]:
                    print(f"    Урока {j} нет в БД")
            elif j =='tasks':
                pass #пока нет в БД
        os.chdir("..")