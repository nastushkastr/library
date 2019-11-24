from flask import session
from flaskr.db.db import group_reader_connect


def do_login(login, password):
    cursor = group_reader_connect().cursor()
    query = "SELECT U_log, U_pass, log, pass FROM users WHERE U_log = %s AND U_pass = %s "
    cursor.execute(query, [login, password])
    account = cursor.fetchone()
    if account:
        session['logged_in'] = True
        session['login'] = account[0]
        session['g_log'] = account[2]
        session['g_pass'] = account[3]
        return True
    return False


def do_logout():
    session.pop('logged_in', None)
    session.pop('login', None)
    session.pop('g_log', None)
    session.pop('g_pass', None)

