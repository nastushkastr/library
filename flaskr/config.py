import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MYSQL_DATABASE_READER_USER = 'group_reader'
    MYSQL_DATABASE_PASSWORD = 'password'
    MYSQL_DATABASE_DB = 'library'
    MYSQL_DATABASE_HOST = 'localhost'
