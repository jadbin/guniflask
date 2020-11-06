# coding=utf-8


import pytest
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref, relationship, sessionmaker

from guniflask.orm import result_to_dict, BaseModelMixin

Base = declarative_base()


class User(BaseModelMixin, Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    nickname = Column(String)


class Article(BaseModelMixin, Base):
    __tablename__ = 'article'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    user_id = Column(Integer, ForeignKey('user.id'))
    author = relationship('User', backref=backref('articles'))


@pytest.fixture
def session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    user = User(id=1, name='Bob', nickname='Good Boy')
    session.add(user)
    article = Article(id=1, title='Happy', content='Happy Day!', author=user)
    session.add(article)
    session.commit()

    return session


def test_result_to_dict(session):
    result = session.query(User).with_entities(User.name, User.nickname).filter_by(name='Bob').all()
    assert result_to_dict(result[0]) == {'name': 'Bob', 'nickname': 'Good Boy'}


def test_model_from_dict():
    article = Article.from_dict(dict(id=1, title='Title'))
    assert article.id == 1
    assert article.title == 'Title'


def test_model_from_dict_with_ignore():
    article = Article.from_dict(dict(id=1, title='Title'), ignore='id')
    assert article.id is None
    assert article.title == 'Title'


def test_model_from_dict_with_only():
    article = Article.from_dict(dict(id=1, title='Title', content='Content'), only='title,content')
    assert article.id is None
    assert article.title == 'Title'
    assert article.content == 'Content'


def test_model_to_dict(session):
    article = session.query(Article).filter_by(id=1).first()
    d = article.to_dict()
    assert d == {'id': 1, 'title': 'Happy', 'content': 'Happy Day!', 'user_id': 1}


def test_model_to_dict_with_ignore(session):
    article = session.query(Article).filter_by(id=1).first()
    d = article.to_dict(ignore='id,user_id')
    assert d == {'title': 'Happy', 'content': 'Happy Day!'}


def test_model_to_dict_with_only(session):
    article = session.query(Article).filter_by(id=1).first()
    d = article.to_dict(only='title,content')
    assert d == {'title': 'Happy', 'content': 'Happy Day!'}


def test_update_model_by_dict():
    article = Article()
    article.update_by_dict(dict(id=1, title='Title'))
    assert article.id == 1
    assert article.title == 'Title'


def test_update_model_by_dict_with_ignore():
    article = Article()
    article.update_by_dict(dict(id=1, title='Title'), ignore='id')
    assert article.id is None
    assert article.title == 'Title'


def test_update_model_by_dict_with_only():
    article = Article()
    article.update_by_dict(dict(id=1, title='Title', content='Content'), only='title,content')
    assert article.id is None
    assert article.title == 'Title'
    assert article.content == 'Content'
