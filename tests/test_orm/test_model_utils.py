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
    article = Article(id=1, title='Title', content='Content', author=user)
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


def test_model_from_dict_with_many_to_one_relation():
    article_data = dict(
        id=1,
        title='Title',
        content='Content',
        user_id=1,
        author=dict(
            id=1,
            name='Bob',
            nickname='Good Boy',
        ),
    )
    article = Article.from_dict(article_data)
    assert article.id == 1
    assert article.title == 'Title'
    assert article.content == 'Content'
    assert article.user_id == 1
    assert article.author.id == 1
    assert article.author.name == 'Bob'
    assert article.author.nickname == 'Good Boy'


def test_model_from_dict_with_one_to_many_relation():
    user_data = dict(
        id=1,
        name='Bob',
        nickname='Good Boy',
        articles=[
            dict(
                id=1,
                title='Title',
                content='Content',
                user_id=1,
            )
        ],
    )
    user = User.from_dict(user_data)
    assert user.id == 1
    assert user.name == 'Bob'
    assert user.nickname == 'Good Boy'
    article = user.articles[0]
    assert article.id == 1
    assert article.title == 'Title'
    assert article.content == 'Content'
    assert article.user_id == 1


def test_model_from_dict_with_ignore():
    article = Article.from_dict(dict(id=1, title='Title'), ignore='id')
    assert article.id is None
    assert article.title == 'Title'


def test_model_from_dict_with_only():
    article = Article.from_dict(dict(id=1, title='Title', content='Content'), only='title,content')
    assert article.id is None
    assert article.title == 'Title'
    assert article.content == 'Content'


def test_model_to_dict():
    article = Article(id=1, title='Title', content='Content', user_id=1,
                      author=User(id=1, name='Bob', nickname='Good Boy'))
    d = article.to_dict(include='author')
    assert d == {'id': 1, 'title': 'Title', 'content': 'Content', 'user_id': 1,
                 'author': {'id': 1, 'name': 'Bob', 'nickname': 'Good Boy'}}


def test_model_to_dict_with_ignore():
    article = Article(id=1, title='Title', content='Content', user_id=1,
                      author=User(id=1, name='Bob', nickname='Good Boy'))
    d = article.to_dict(ignore='id,user_id,author.id', include='author')
    assert d == {'title': 'Title', 'content': 'Content',
                 'author': {'name': 'Bob', 'nickname': 'Good Boy'}}


def test_model_to_dict_with_only():
    article = Article(id=1, title='Title', content='Content', user_id=1,
                      author=User(id=1, name='Bob', nickname='Good Boy'))
    d = article.to_dict(only='title,content,author.name,author.nickname', include='author')
    assert d == {'title': 'Title', 'content': 'Content',
                 'author': {'name': 'Bob', 'nickname': 'Good Boy'}}


def test_model_to_dict_with_one_to_many_relation(session):
    user = session.query(User).filter_by(id=1).first()
    d = user.to_dict(include='articles')
    assert d == {'id': 1, 'name': 'Bob', 'nickname': 'Good Boy',
                 'articles': [{'id': 1, 'title': 'Title', 'content': 'Content', 'user_id': 1}]}


def test_model_to_dict_with_many_to_one_relation(session):
    article = session.query(Article).filter_by(id=1).first()
    d = article.to_dict(include='author')
    assert d == {'id': 1, 'title': 'Title', 'content': 'Content', 'user_id': 1,
                 'author': {'id': 1, 'name': 'Bob', 'nickname': 'Good Boy'}}


def test_update_model_by_dict():
    article = Article()
    article.update_by_dict(dict(id=1, title='Title', author=dict(id=1, name='Bob')))
    assert article.id == 1
    assert article.title == 'Title'
    assert article.author.id == 1
    assert article.author.name == 'Bob'


def test_update_model_by_dict_with_ignore():
    article = Article(author=User())
    article.update_by_dict(dict(id=1, title='Title', author=dict(id=1, name='Bob')), ignore='id,author.id')
    assert article.id is None
    assert article.title == 'Title'
    assert article.author.id is None
    assert article.author.name == 'Bob'


def test_update_model_by_dict_with_only():
    article = Article()
    article.update_by_dict(
        dict(
            id=1,
            title='Title',
            content='Content',
            author=dict(id=1, name='Bob'),
        ),
        only='title,content,author.name',
    )
    assert article.id is None
    assert article.title == 'Title'
    assert article.content == 'Content'
    assert article.author.id is None
    assert article.author.name == 'Bob'


def test_update_model_by_dict_with_list():
    user = User()
    with pytest.raises(RuntimeError):
        user.update_by_dict({'name': 'Bob', 'articles': [{'title': 'Title'}]})
