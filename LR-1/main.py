from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
import sys


class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    age: int
    course: int  # 1-6
    faculty: str


sqlite_file_name = "students.db"
engine = create_engine(f"sqlite:///{sqlite_file_name}", echo=False)


def create_db():
    SQLModel.metadata.create_all(engine)


def add_student():
    print("\nДобавление студента")
    name = input("ФИО: ")
    age = int(input("Возраст: "))
    course = int(input("Курс: "))
    faculty = input("Факультет: ")

    student = Student(
        full_name=name,
        age=age,
        course=course,
        faculty=faculty
    )

    with Session(engine) as session:
        session.add(student)
        session.commit()
        print("Студент добавлен!")


def list_students():
    print("\nСписок студентов:")

    with Session(engine) as session:
        students = session.exec(select(Student)).all()

        if not students:
            print("Нет записей.")
            return

        for s in students:
            print(f"[{s.id}] {s.full_name} | {s.age} лет | {s.course} курс | {s.faculty}")


def delete_student():
    student_id = int(input("Введите ID студента для удаления: "))

    with Session(engine) as session:
        student = session.get(Student, student_id)

        if not student:
            print("Студент не найден")
            return

        session.delete(student)
        session.commit()
        print("Студент удалён")


def menu():
    while True:
        print("\n=== Учёт студентов ВУЗа ===")
        print("1. Добавить студента")
        print("2. Показать всех студентов")
        print("3. Удалить студента")
        print("0. Выход")

        choice = input("Выберите действие: ")

        if choice == "1":
            add_student()
        elif choice == "2":
            list_students()
        elif choice == "3":
            delete_student()
        elif choice == "0":
            print("Выход...")
            sys.exit()
        else:
            print("Неверный выбор!")


if __name__ == "__main__":
    create_db()
    menu()