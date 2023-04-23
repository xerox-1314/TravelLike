import datetime
import sqlalchemy
from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase):
    __tablename__ = 'news'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    place = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    images = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    likes = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    dislikes = sqlalchemy.Column(sqlalchemy.Integer, nullable=True, default=0)
    created_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    user = sqlalchemy.orm.relationship('User')