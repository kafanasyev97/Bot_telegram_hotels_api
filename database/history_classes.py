from peewee import *


db = SqliteDatabase('data.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    class Meta:
        db_table = 'users'
    command = CharField()
    date = CharField()
    user_id = IntegerField()


class Hotel(BaseModel):
    class Meta:
        db_table = 'hotels'
    name = CharField()
    address = CharField()
    price = CharField()
    distance = CharField()
    req = ForeignKeyField(User, related_name='hotels')
