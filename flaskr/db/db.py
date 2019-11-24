from mysql.connector import connect
from flask import g, session
from flaskr.app.app import app
from flaskr.auth.checkers import is_logged_in


def group_reader_connect():
    if "group_reader_conn" not in g:
        conn = connect(user=app.config['MYSQL_DATABASE_READER_USER'],
                       password=app.config['MYSQL_DATABASE_PASSWORD'],
                       host=app.config['MYSQL_DATABASE_HOST'],
                       database=app.config['MYSQL_DATABASE_DB'])
        g.group_reader_conn = conn
    return g.group_reader_conn


@app.teardown_appcontext
def close_db(exception):
    if "group_reader_conn" in g:
        g.group_reader_conn.close()
        del g.group_reader_conn
    if "group_conn" in g:
        g.group_conn.close()
        del g.group_conn
    if exception:
        raise exception


def group_connect():
    if not is_logged_in():
        return None
    if "group_conn" not in g:
        conn = connect(user=session["g_log"],
                       password=session["g_pass"],
                       host=app.config['MYSQL_DATABASE_HOST'],
                       database=app.config['MYSQL_DATABASE_DB'])
        g.group_conn = conn
    return g.group_conn
