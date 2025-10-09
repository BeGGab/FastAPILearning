import sqlalchemy as sa
from typing import List
import uuid
from sqlalchemy.orm import DeclarativeMeta, declarative_base, declared_attr
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs

from src.db import uniq_str_an, created_at, updated_at




metadata = sa.MetaData()


class BaseServiceModel(AsyncAttrs):
    __abstract__ = True

    '''@declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()'''
    
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    """Базовый класс для таблиц сервиса."""

    @classmethod
    def on_conflict_constraint(cls) -> tuple | None:
        return None


Base: DeclarativeMeta = declarative_base(metadata=metadata, cls=BaseServiceModel)


class Author(Base):
    __tablename__ = 'authors'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[uniq_str_an] = mapped_column(nullable=False)
    boi: Mapped[str] = mapped_column(sa.Text())

    books: Mapped[List['Book']] = relationship(
        secondary='author_book', back_populates='authors'
    )


class Book(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(), nullable=False)
    description: Mapped[str] = mapped_column(sa.Text())
    publication_year: Mapped[int]
    
    authors: Mapped[List['Author']] = relationship(
        secondary='author_book', back_populates='books'
    )


class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4())
    username: Mapped[uniq_str_an]
    email: Mapped[uniq_str_an]
    phone_number: Mapped[uniq_str_an]

    profile: Mapped['Profile'] = relationship(
        back_populates='user',
        uselist=False,
        cascade='all, delete-orphan'
    )

class Profile(Base):
    __tablename__ = 'profiles'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4())
    full_name: Mapped[str] = mapped_column(sa.String(), nullable=True)
    bio: Mapped[str] = mapped_column(sa.Text())
    user_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey('users.id', ondelete='CASCADE'), unique=True)

    user: Mapped['User'] = relationship(
        back_populates='profile'
    )

class Department(Base):
    __tablename__ = 'departments'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(), nullable=True)
    description: Mapped[str] = mapped_column(sa.Text())

    employees: Mapped[List['Employee']] = relationship(
        back_populates="department",
        cascade="all, delete-orphan"
    )

class Employee(Base):
    __tablename__ = 'employees'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[uniq_str_an] 
    position: Mapped[str] = mapped_column(sa.String())
    department_id: Mapped[uuid.UUID] = mapped_column(sa.ForeignKey('departments.id', ondelete='CASCADE'))

    department: Mapped['Department'] = relationship(
        back_populates="employees"
    )


# Определение ассоциативной таблицы ПОСЛЕ определения основных моделей
author_book_association = sa.Table(
    'author_book',
    Base.metadata,
    sa.Column('author_id', sa.ForeignKey('authors.id')),
    sa.Column('book_id', sa.ForeignKey('books.id'))
)
