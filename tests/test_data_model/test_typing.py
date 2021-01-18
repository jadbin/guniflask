import inspect
from typing import List, Set, Mapping, Dict

import pytest

from guniflask.data_model.typing import parse_json, analyze_arg_type, inspect_args


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


def test_parse_simple_data():
    assert parse_json('1', dtype=int) == 1
    assert parse_json('1', dtype=List[int]) == [1]
    assert parse_json([1, 2, 3]) == [1, 2, 3]
    assert parse_json({'key': 'value'}) == {'key': 'value'}


def test_parse_object_data():
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

    student = parse_json(student_data, Student)

    assert isinstance(student, Student)
    assert student.name == 'Bob'
    assert student.age == 12
    assert student.graduated is True
    assert student.hobbies == ['Programming', 'Piano']
    assert student.scores == {'Math': 100}
    assert not hasattr(student, 'secret')

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


def test_analyze_arg_type():
    arg_ = analyze_arg_type(None)
    assert arg_.is_singleton() and arg_.outer_type is None

    with pytest.raises(ValueError):
        analyze_arg_type('')

    arg_ = analyze_arg_type(list)
    assert arg_.is_list() and arg_.outer_type is None

    arg_ = analyze_arg_type(set)
    assert arg_.is_set() and arg_.outer_type is None

    arg_ = analyze_arg_type(dict)
    assert arg_.is_dict() and arg_.outer_type == (None, None)

    arg_ = analyze_arg_type(int)
    assert arg_.is_singleton() and arg_.outer_type is int

    arg_ = analyze_arg_type(str)
    assert arg_.is_singleton() and arg_.outer_type is str

    arg_ = analyze_arg_type(List)
    assert arg_.is_list() and arg_.outer_type is None

    arg_ = analyze_arg_type(Set)
    assert arg_.is_set() and arg_.outer_type is None

    arg_ = analyze_arg_type(Mapping)
    assert arg_.is_dict() and arg_.outer_type == (None, None)

    arg_ = analyze_arg_type(Dict)
    assert arg_.is_dict() and arg_.outer_type == (None, None)

    class A:
        pass

    arg_ = analyze_arg_type(A)
    assert arg_.is_singleton() and arg_.outer_type is A

    arg_ = analyze_arg_type(List[A])
    assert arg_.is_list() and arg_.outer_type is A
    arg_ = analyze_arg_type(List[str])
    assert arg_.is_list() and arg_.outer_type is str

    arg_ = analyze_arg_type(Set[A])
    assert arg_.is_set() and arg_.outer_type is A
    arg_ = analyze_arg_type(Set[str])
    assert arg_.is_set() and arg_.outer_type is str

    arg_ = analyze_arg_type(Mapping[str, A])
    assert arg_.is_dict() and arg_.outer_type == (str, A)
    arg_ = analyze_arg_type(Mapping[str, str])
    assert arg_.is_dict() and arg_.outer_type == (str, str)

    arg_ = analyze_arg_type(Dict[str, A])
    assert arg_.is_dict() and arg_.outer_type == (str, A)
    arg_ = analyze_arg_type(Dict[str, str])
    assert arg_.is_dict() and arg_.outer_type == (str, str)

    arg_ = analyze_arg_type(Mapping[str, List[A]])
    assert arg_.is_dict() and type(arg_.outer_type) == tuple
    outer_type = arg_.outer_type
    assert outer_type[0] == str
    assert outer_type[1].is_list() and outer_type[1].outer_type == A


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
