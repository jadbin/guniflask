from typing import List

from guniflask.data_model import DataModel


class Person(DataModel):
    name: str
    age: int = None


class Student(Person):
    graduate: bool = None


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


class User(DataModel):
    name: str


class Article(DataModel):
    title: str
    author: User = None


def test_data_model_from_dict_with_many_to_one():
    d = Article.from_dict(dict(title='Title', author=dict(name='Bob')))
    assert d.title == 'Title'
    assert d.author.name == 'Bob'


def test_data_model_to_dict_with_many_to_one():
    d = Article.from_dict(dict(title='Title', author=dict(name='Bob'))).to_dict()
    assert d == {
        'title': 'Title',
        'author': {
            'name': 'Bob',
        },
    }


class ArticleSet(DataModel):
    name: str
    articles: List[Article]


def test_data_model_from_dict_with_one_to_many():
    d = ArticleSet.from_dict(dict(name='Name', articles=[dict(title='Title')]))
    assert d.name == 'Name'
    assert len(d.articles) == 1
    assert d.articles[0].title == 'Title'


def test_data_model_to_dict_with_one_to_many():
    article_set = ArticleSet.from_dict(dict(name='Name', articles=[dict(title='Title')]))

    d = article_set.to_dict()
    assert d == {
        'name': 'Name',
        'articles': [
            {
                'title': 'Title',
                'author': None,
            }
        ],
    }

    d = article_set.to_dict(ignore='articles.author')
    assert d == {
        'name': 'Name',
        'articles': [
            {
                'title': 'Title',
            }
        ],
    }

    d = article_set.to_dict(ignore='articles')
    assert d == {
        'name': 'Name',
    }

    d = article_set.to_dict(only='articles.title')
    assert d == {
        'articles': [
            {
                'title': 'Title',
            }
        ]
    }
