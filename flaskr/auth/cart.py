from flask import session


def get_cart():
    if 'cart' not in session:
        session['cart'] = {}
        session.modified = True
    return session['cart']


def del_from_cart(e_id):
    del get_cart()[e_id]
    session.modified = True


def add_to_cart(e_id, count):
    s_cart = get_cart()
    if e_id not in s_cart:
        s_cart[e_id] = 0
    s_cart[e_id] += count
    session.modified = True


def put_to_cart(e_id, count):
    if count > 0:
        get_cart()[e_id] = count
    else:
        del_from_cart(e_id)
    session.modified = True


def cart_clear():
    if 'cart' in session:
        session['cart'] = {}
