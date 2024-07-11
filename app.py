import sqlite3
import streamlit as st
import pandas as pd
import json

# Создаем базу данных в памяти
conn = sqlite3.connect(':memory:')
cursor = conn.cursor()

# Создаем таблицы и заполняем данными
cursor.execute('''CREATE TABLE Students (
    StudentID INTEGER PRIMARY KEY,
    LastName TEXT,
    FirstName TEXT,
    GroupNumber INTEGER,
    Course INTEGER
)''')

cursor.execute('''CREATE TABLE Subjects (
    SubjectID INTEGER PRIMARY KEY,
    SubjectName TEXT
)''')

cursor.execute('''CREATE TABLE Grades (
    GradeID INTEGER PRIMARY KEY,
    StudentID INTEGER,
    SubjectID INTEGER,
    TeacherID INTEGER,
    Grade INTEGER,
    FOREIGN KEY (StudentID) REFERENCES Students (StudentID),
    FOREIGN KEY (SubjectID) REFERENCES Subjects (SubjectID),
    FOREIGN KEY (TeacherID) REFERENCES Teachers (TeacherID)
)''')

cursor.execute('''CREATE TABLE Teachers (
    TeacherID INTEGER PRIMARY KEY,
    LastName TEXT,
    FirstName TEXT
)''')

cursor.execute('''CREATE TABLE TeachersSubjects (
    TeacherSubjectID INTEGER PRIMARY KEY,
    TeacherID INTEGER,
    SubjectID INTEGER,
    FOREIGN KEY (TeacherID) REFERENCES Teachers (TeacherID),
    FOREIGN KEY (SubjectID) REFERENCES Subjects (SubjectID)
)''')

students = [
    (1, 'Иванов', 'Иван', 101, 1),
    (2, 'Петров', 'Петр', 102, 2),
    (3, 'Сидоров', 'Алексей', 101, 1),
    (4, 'Смирнова', 'Мария', 103, 3),
    (5, 'Кузнецова', 'Елена', 104, 4)
]

subjects = [
    (1, 'Математика'),
    (2, 'Физика'),
    (3, 'Химия'),
    (4, 'Биология'),
    (5, 'Литература')
]

grades = [
    (1, 1, 1, 1, 5),
    (2, 1, 2, 2, 4),
    (3, 2, 1, 1, 3),
    (4, 2, 3, 3, 5),
    (5, 3, 4, 4, 4),
    (6, 3, 1, 5, 3),
    (7, 4, 1, 1, 3),
    (8, 4, 5, 5, 3),
    (9, 5, 1, 1, 3),
    (10, 5, 3, 1, 3),
    (11, 5, 2, 2, 4)
]

teachers = [
    (1, 'Смирнов', 'Сергей'),
    (2, 'Кузнецов', 'Игорь'),
    (3, 'Иванова', 'Анна'),
    (4, 'Петрова', 'Ольга'),
    (5, 'Сидорова', 'Елена')
]

teachers_subjects = [
    (1, 1, 1),
    (2, 2, 2),
    (3, 3, 3),
    (4, 4, 4),
    (5, 5, 5),
    (6, 5, 1),
    (7, 1, 3),
    (8, 1, 5),
]

cursor.executemany('INSERT INTO Students VALUES (?, ?, ?, ?, ?)', students)
cursor.executemany('INSERT INTO Subjects VALUES (?, ?)', subjects)
cursor.executemany('INSERT INTO Grades VALUES (?, ?, ?, ?, ?)', grades)
cursor.executemany('INSERT INTO Teachers VALUES (?, ?, ?)', teachers)
cursor.executemany('INSERT INTO TeachersSubjects VALUES (?, ?, ?)', teachers_subjects)

conn.commit()

# Создаем интерфейс
st.title("Университет")

# Выбор фильтра
filter_option = st.selectbox("Выберите фильтр", ["Студент", "Преподаватель", "Предмет"])

if filter_option == "Студент":
    student_names = cursor.execute('SELECT LastName || " " || FirstName FROM Students').fetchall()
    student_names = [name[0] for name in student_names]
    selected_student = st.selectbox("Выберите студента", student_names)
    
    if selected_student:
        last_name, first_name = selected_student.split()
        student_info = cursor.execute('''
            SELECT Students.LastName, Students.FirstName, Students.GroupNumber, Students.Course, 
                   Subjects.SubjectName, Grades.Grade, Teachers.LastName || " " || Teachers.FirstName AS Teacher
            FROM Students
            JOIN Grades ON Students.StudentID = Grades.StudentID
            JOIN Subjects ON Grades.SubjectID = Subjects.SubjectID
            JOIN Teachers ON Grades.TeacherID = Teachers.TeacherID
            WHERE Students.LastName = ? AND Students.FirstName = ?
        ''', (last_name, first_name)).fetchall()

        df_student = pd.DataFrame(student_info, columns=["LastName", "FirstName", "GroupNumber", "Course", "Subject", "Grade", "Teacher"])
        st.write(df_student)
        result_json = df_student.to_json(orient='records', force_ascii=False)
        st.json(json.loads(result_json))

elif filter_option == "Преподаватель":
    teacher_names = cursor.execute('SELECT LastName || " " || FirstName FROM Teachers').fetchall()
    teacher_names = [name[0] for name in teacher_names]
    selected_teacher = st.selectbox("Выберите преподавателя", teacher_names)
    
    if selected_teacher:
        last_name, first_name = selected_teacher.split()
        teacher_info = cursor.execute('''
            SELECT Teachers.LastName, Teachers.FirstName, 
                   Students.LastName || " " || Students.FirstName AS Student, 
                   Subjects.SubjectName, Grades.Grade
            FROM Teachers
            JOIN TeachersSubjects ON Teachers.TeacherID = TeachersSubjects.TeacherID
            JOIN Subjects ON TeachersSubjects.SubjectID = Subjects.SubjectID
            JOIN Grades ON TeachersSubjects.TeacherID = Grades.TeacherID AND TeachersSubjects.SubjectID = Grades.SubjectID
            JOIN Students ON Grades.StudentID = Students.StudentID
            WHERE Teachers.LastName = ? AND Teachers.FirstName = ?
        ''', (last_name, first_name)).fetchall()

        df_teacher = pd.DataFrame(teacher_info, columns=["TeacherLastName", "TeacherFirstName", "Student", "Subject", "Grade"])
        st.write(df_teacher)
        result_json = df_teacher.to_json(orient='records', force_ascii=False)
        st.json(json.loads(result_json))

elif filter_option == "Предмет":
    subject_names = cursor.execute('SELECT SubjectName FROM Subjects').fetchall()
    subject_names = [name[0] for name in subject_names]
    selected_subject = st.selectbox("Выберите предмет", subject_names)
    
    if selected_subject:
        subject_info = cursor.execute('''
            SELECT Subjects.SubjectName, 
                   Teachers.LastName || " " || Teachers.FirstName AS Teacher, 
                   Students.LastName || " " || Students.FirstName AS Student, 
                   Grades.Grade
            FROM Subjects
            JOIN TeachersSubjects ON Subjects.SubjectID = TeachersSubjects.SubjectID
            JOIN Teachers ON TeachersSubjects.TeacherID = Teachers.TeacherID
            JOIN Grades ON Subjects.SubjectID = Grades.SubjectID AND Teachers.TeacherID = Grades.TeacherID
            JOIN Students ON Grades.StudentID = Students.StudentID
            WHERE Subjects.SubjectName = ?
        ''', (selected_subject,)).fetchall()

        df_subject = pd.DataFrame(subject_info, columns=["Subject", "Teacher", "Student", "Grade"])
        st.write(df_subject)
        result_json = df_subject.to_json(orient='records', force_ascii=False)
        st.json(json.loads(result_json))

# Закрываем соединение с базой данных
conn.close()