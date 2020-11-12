import inspect
from typing import List, Set, Mapping, Dict, Union

import pytest

from guniflask.data_model.mapping import map_json, resolve_arg_type, ArgType, inspect_args


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


def test_resolve_arg_type():
    c, t = resolve_arg_type(None)
    assert c is ArgType.SINGLE, t is None

    with pytest.raises(ValueError):
        resolve_arg_type('')

    with pytest.raises(ValueError):
        resolve_arg_type(Union[int, str])

    c, t = resolve_arg_type(list)
    assert c is ArgType.LIST, t is None

    c, t = resolve_arg_type(set)
    assert c is ArgType.SET, t is None

    c, t = resolve_arg_type(dict)
    assert c is ArgType.DICT, t is None

    c, t = resolve_arg_type(int)
    assert c is ArgType.SINGLE, t is int

    c, t = resolve_arg_type(str)
    assert c is ArgType.SINGLE, t is str

    c, t = resolve_arg_type(List)
    assert c is ArgType.LIST, t is None

    c, t = resolve_arg_type(Set)
    assert c is ArgType.SET, t is None

    c, t = resolve_arg_type(Mapping)
    assert c is ArgType.DICT, t is None

    c, t = resolve_arg_type(Dict)
    assert c is ArgType.DICT, t is None

    class A:
        pass

    c, t = resolve_arg_type(A)
    assert c is ArgType.SINGLE, t is A

    c, t = resolve_arg_type(List[A])
    assert c is ArgType.LIST, t is A
    c, t = resolve_arg_type(List[str])
    assert c is ArgType.LIST, t is str

    c, t = resolve_arg_type(Set[A])
    assert c is ArgType.SET, t is A
    c, t = resolve_arg_type(Set[str])
    assert c is ArgType.SET, t is str

    c, t = resolve_arg_type(Mapping[str, A])
    assert c is ArgType.DICT, t == (str, A)
    c, t = resolve_arg_type(Mapping[str, str])
    assert c is ArgType.DICT, t == (str, str)

    c, t = resolve_arg_type(Dict[str, A])
    assert c is ArgType.DICT, t == (str, A)
    c, t = resolve_arg_type(Dict[str, str])
    assert c is ArgType.DICT, t == (str, str)


def test_inspect_args():
    class A:
        pass

    def func(a, b: int, c: List, d=1, e: List = None, f: List[str] = None, g: A = None) -> dict:
        pass

    args, hints = inspect_args(func)
    assert args['a'] is inspect._empty
    assert args['b'] is inspect._empty
    assert args['c'] is inspect._empty
    assert args['d'] == 1
    assert args['e'] is None
    assert args['f'] is None
    assert args['g'] is None
    assert hints == {'return': dict, 'b': int, 'c': List, 'e': List, 'f': List[str], 'g': A}
