from functools import wraps
from flask import session, abort


def is_logged_in():
    if 'logged_in' in session and session['logged_in']:
        return True
    return False


def get_group():
    if is_logged_in():
        return session['g_log']
    return None


def in_group(groups):
    def _in_group(f):
        @wraps(f)
        def inner(*args, **kwargs):
            if get_group() in groups:
                return f(*args, **kwargs)
            return abort(403)
        return inner
    return _in_group
