# coding=utf-8

from guniflask.data_model import DataModel


class Person(DataModel):
    name: str
    age: int


class Student(Person):
    graduate: bool


def test_create_data_model():
    student = Student(name='Bob', graduate=True)
    assert student.name == 'Bob'
    assert student.age is None
    assert student.graduate is True


def test_data_model_from_dict():
    student = Student.from_dict(dict(name='Bob', graduate=True))
    assert student.name == 'Bob'
    assert student.age is None
    assert student.graduate is True


def test_data_model_to_dict():
    d = Student.from_dict(dict(name='Bob', graduate=True)).to_dict()
    assert d['name'] == 'Bob'
    assert d['age'] is None
    assert d['graduate'] is True
