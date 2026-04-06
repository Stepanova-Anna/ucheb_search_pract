"""
Student Database System - система учёта обучающихся.
Методология: Agile (итеративная разработка)
Методы: нормализация БД, параметризованные SQL-запросы, JOIN, агрегация.
"""

import sqlite3
import sys
from datetime import datetime


class StudentDB:
    """Класс для работы с базой данных обучающихся."""

    def __init__(self, db_name="students.db"):
        """Инициализация подключения и создание таблиц."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        """Метод: создание таблиц (нормализованная структура)."""
        # Таблица студентов
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                group_name TEXT NOT NULL,
                birth_date TEXT,
                email TEXT UNIQUE
            )
        ''')

        # Таблица дисциплин
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                teacher TEXT
            )
        ''')

        # Таблица оценок (связь студент-дисциплина)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS grades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER,
                subject_id INTEGER,
                grade INTEGER CHECK(grade >= 2 AND grade <= 5),
                date TEXT,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    # ---------- СТУДЕНТЫ (CRUD) ----------
    def add_student(self, full_name, group_name, birth_date, email):
        """Метод: добавить студента."""
        try:
            self.cursor.execute('''
                INSERT INTO students (full_name, group_name, birth_date, email)
                VALUES (?, ?, ?, ?)
            ''', (full_name, group_name, birth_date, email))
            self.conn.commit()
            print(f"✓ Студент '{full_name}' добавлен (ID: {self.cursor.lastrowid})")
        except sqlite3.IntegrityError:
            print("✗ Ошибка: студент с таким email уже существует")

    def list_students(self):
        """Метод: показать всех студентов."""
        self.cursor.execute("SELECT id, full_name, group_name, email FROM students")
        students = self.cursor.fetchall()
        if not students:
            print("Список студентов пуст.")
            return
        print("\n=== СПИСОК СТУДЕНТОВ ===")
        for s in students:
            print(f"ID: {s[0]} | {s[1]} | Группа: {s[2]} | Email: {s[3]}")

    def update_student(self, student_id, **kwargs):
        """Метод: обновить данные студента."""
        allowed_fields = {'full_name', 'group_name', 'birth_date', 'email'}
        for field, value in kwargs.items():
            if field in allowed_fields:
                self.cursor.execute(f"UPDATE students SET {field}=? WHERE id=?", (value, student_id))
        self.conn.commit()
        print(f"✓ Студент ID {student_id} обновлён")

    def delete_student(self, student_id):
        """Метод: удалить студента (каскадно удалятся оценки)."""
        self.cursor.execute("DELETE FROM students WHERE id=?", (student_id,))
        self.conn.commit()
        print(f"✓ Студент ID {student_id} удалён")

    # ---------- ДИСЦИПЛИНЫ (CRUD) ----------
    def add_subject(self, name, teacher=""):
        """Метод: добавить дисциплину."""
        try:
            self.cursor.execute("INSERT INTO subjects (name, teacher) VALUES (?, ?)", (name, teacher))
            self.conn.commit()
            print(f"✓ Дисциплина '{name}' добавлена")
        except sqlite3.IntegrityError:
            print("✗ Ошибка: такая дисциплина уже существует")

    def list_subjects(self):
        """Метод: показать все дисциплины."""
        self.cursor.execute("SELECT id, name, teacher FROM subjects")
        subjects = self.cursor.fetchall()
        if not subjects:
            print("Список дисциплин пуст.")
            return
        print("\n=== СПИСОК ДИСЦИПЛИН ===")
        for s in subjects:
            print(f"ID: {s[0]} | {s[1]} | Преподаватель: {s[2] or 'не указан'}")

    # ---------- ОЦЕНКИ ----------
    def add_grade(self, student_id, subject_id, grade):
        """Метод: выставить оценку."""
        if grade < 2 or grade > 5:
            print("✗ Оценка должна быть от 2 до 5")
            return
        date = datetime.now().strftime("%Y-%m-%d")
        self.cursor.execute('''
            INSERT INTO grades (student_id, subject_id, grade, date)
            VALUES (?, ?, ?, ?)
        ''', (student_id, subject_id, grade, date))
        self.conn.commit()
        print(f"✓ Оценка {grade} выставлена студенту ID {student_id} по предмету ID {subject_id}")

    def student_performance(self, student_id):
        """Метод: успеваемость студента (средний балл + список оценок)."""
        # Средний балл
        self.cursor.execute('''
            SELECT AVG(grade) FROM grades WHERE student_id=?
        ''', (student_id,))
        avg_grade = self.cursor.fetchone()[0]

        # Детальный список оценок с названиями предметов
        self.cursor.execute('''
            SELECT subjects.name, grades.grade, grades.date
            FROM grades
            JOIN subjects ON grades.subject_id = subjects.id
            WHERE grades.student_id=?
            ORDER BY grades.date DESC
        ''', (student_id,))
        grades_list = self.cursor.fetchall()

        print(f"\n=== УСПЕВАЕМОСТЬ СТУДЕНТА ID {student_id} ===")
        if avg_grade:
            print(f"Средний балл: {avg_grade:.2f}")
        else:
            print("Оценок пока нет")

        if grades_list:
            print("\nОценки по предметам:")
            for subj_name, grade, date in grades_list:
                print(f"  {subj_name}: {grade} (от {date})")

    def close(self):
        """Закрыть соединение с БД."""
        self.conn.close()


# ---------- КОНСОЛЬНЫЙ ИНТЕРФЕЙС ----------
def print_menu():
    print("\n" + "=" * 40)
    print("СИСТЕМА УЧЁТА ОБУЧАЮЩИХСЯ")
    print("=" * 40)
    print("1. Список студентов")
    print("2. Добавить студента")
    print("3. Редактировать студента")
    print("4. Удалить студента")
    print("5. Список дисциплин")
    print("6. Добавить дисциплину")
    print("7. Выставить оценку")
    print("8. Посмотреть успеваемость студента")
    print("0. Выход")
    print("=" * 40)


def main():
    db = StudentDB()

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()

        if choice == "1":
            db.list_students()

        elif choice == "2":
            name = input("ФИО: ")
            group = input("Группа: ")
            birth = input("Дата рождения (ГГГГ-ММ-ДД): ")
            email = input("Email: ")
            db.add_student(name, group, birth, email)

        elif choice == "3":
            db.list_students()
            sid = int(input("ID студента для редактирования: "))
            print("Оставьте поле пустым, если не хотите менять")
            name = input("Новое ФИО: ")
            group = input("Новая группа: ")
            birth = input("Новая дата рождения: ")
            email = input("Новый email: ")
            if name: db.update_student(sid, full_name=name)
            if group: db.update_student(sid, group_name=group)
            if birth: db.update_student(sid, birth_date=birth)
            if email: db.update_student(sid, email=email)

        elif choice == "4":
            db.list_students()
            sid = int(input("ID студента для удаления: "))
            db.delete_student(sid)

        elif choice == "5":
            db.list_subjects()

        elif choice == "6":
            name = input("Название дисциплины: ")
            teacher = input("Преподаватель (необязательно): ")
            db.add_subject(name, teacher)

        elif choice == "7":
            db.list_students()
            sid = int(input("ID студента: "))
            db.list_subjects()
            subj_id = int(input("ID дисциплины: "))
            grade = int(input("Оценка (2-5): "))
            db.add_grade(sid, subj_id, grade)

        elif choice == "8":
            db.list_students()
            sid = int(input("ID студента: "))
            db.student_performance(sid)

        elif choice == "0":
            print("До свидания!")
            db.close()
            sys.exit(0)

        else:
            print("Неверный выбор. Попробуйте снова.")

        input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()