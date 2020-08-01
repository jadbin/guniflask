# coding=utf-8

from typing import List, Set

from guniflask.utils.instantiation import instantiate_from_json


class Person:
    name: str
    age: int


class Teacher(Person):
    classes: Set


class Student(Person):
    secret: str
    mentor: Teacher
    parents: List[Person]
    scores: dict

    def __init__(self):
        self.hobbies: List = None
        self.graduated = False


def test_instantiate_from_json():
    assert instantiate_from_json('1', dtype=int) == 1
    assert instantiate_from_json([1, 2, 3]) == [1, 2, 3]
    assert instantiate_from_json({'key': 'value'}) == {'key': 'value'}

    student_data = dict(
        name='Xiao Ming',
        age=12,
        graduated=True,
        hobbies=['Programming', 'Piano'],
        scores={'Math': 100},
        parents=[
            dict(
                name='Wang Shu',
                age=40
            ),
            dict(
                name='Wang Shener',
                age=39
            )
        ],
        mentor=dict(
            name='Jia Meng',
            age=41,
            classes=['English', 'Yuwen']
        )
    )

    student = instantiate_from_json(student_data, Student)

    assert isinstance(student, Student)
    assert student.name == 'Xiao Ming'
    assert student.age == 12
    assert student.graduated is True
    assert student.hobbies == ['Programming', 'Piano']
    assert student.scores == {'Math': 100}
    assert student.secret is None

    assert isinstance(student.parents, list) and len(student.parents) == 2
    for parent in student.parents:
        if parent.name == 'Wang Shu':
            assert parent.age == 40
        elif parent.name == 'Wang Shener':
            assert parent.age == 39
        else:
            raise RuntimeError

    assert isinstance(student.mentor, Teacher)
    mentor = student.mentor
    assert mentor.name == 'Jia Meng'
    assert mentor.age == 41
    assert isinstance(mentor.classes, set)
    assert mentor.classes == {'English', 'Yuwen'}
