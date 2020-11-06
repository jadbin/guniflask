# coding=utf-8

from typing import List, Set

from guniflask.data_model.mapping import map_json


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
    hobbies: List = None
    graduated: bool = False


def test_map_simple_data():
    assert map_json('1', dtype=int) == 1
    assert map_json([1, 2, 3]) == [1, 2, 3]
    assert map_json({'key': 'value'}) == {'key': 'value'}


def test_map_object_data():
    student_data = dict(
        name='Bob',
        age=12,
        graduated=True,
        hobbies=['Programming', 'Piano'],
        scores={'Math': 100},
        parents=[
            dict(
                name='Billy',
                age=40
            ),
            dict(
                name='Judy',
                age=39
            )
        ],
        mentor=dict(
            name='Alice',
            age=41,
            classes=['English', 'Math']
        )
    )

    student = map_json(student_data, Student)

    assert isinstance(student, Student)
    assert student.name == 'Bob'
    assert student.age == 12
    assert student.graduated is True
    assert student.hobbies == ['Programming', 'Piano']
    assert student.scores == {'Math': 100}
    assert student.secret is None

    assert isinstance(student.parents, list) and len(student.parents) == 2
    for parent in student.parents:
        if parent.name == 'Billy':
            assert parent.age == 40
        elif parent.name == 'Judy':
            assert parent.age == 39
        else:
            raise RuntimeError

    assert isinstance(student.mentor, Teacher)
    mentor = student.mentor
    assert mentor.name == 'Alice'
    assert mentor.age == 41
    assert isinstance(mentor.classes, set)
    assert mentor.classes == {'English', 'Math'}
