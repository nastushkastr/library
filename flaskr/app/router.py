from flask import render_template, redirect, request, abort
from flaskr.forms import *
from flaskr.auth.auth import do_login, do_logout
from flaskr.auth.checkers import in_group
from flaskr.auth.cart import add_to_cart, put_to_cart, del_from_cart
from .app import app
from .utils import *


@app.route('/')
@app.route('/index')
def index():
    render_ctx = {}
    add_base(render_ctx)
    add_group_menu(render_ctx)
    return render_template('menu.html', **render_ctx)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if is_logged_in():
        return redirect('/')
    form = LoginForm()
    if not form.validate_on_submit():
        return render_template('login.html', title='Sign In', form=form)
    if do_login(form.username.data, form.password.data):
        return redirect('/')
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout', methods=['GET'])
def logout():
    do_logout()
    return redirect('/')


@app.route('/publishers')
@in_group(("watcher", ))
def publisher():
    render_ctx = {}
    add_base(render_ctx)
    add_publishers(render_ctx)
    return render_template('order.html', **render_ctx)


@app.route('/requests/')
@in_group(("watcher", ))
def requests():
    render_ctx = {}
    add_base(render_ctx)
    return render_template('requests.html', **render_ctx)


@app.route('/requests/one/')
@in_group(("watcher", ))
def requests_one():
    render_ctx = {}
    add_base(render_ctx)
    if 'date' in request.args and 'book' in request.args:
        add_requests_one(render_ctx, request.args['date'], request.args['book'])
        return render_template("requests_one_report.html", **render_ctx)
    return render_template('requests_one_form.html', **render_ctx)


@app.route('/requests/two/')
@in_group(("watcher", ))
def requests_two():
    render_ctx = {}
    add_base(render_ctx)
    if 'date' in request.args and 'half_year' in request.args:
        add_requests_two(render_ctx, request.args['date'], request.args['half_year'])
        return render_template("requests_two_report.html", **render_ctx)
    return render_template('requests_two_form.html', **render_ctx)


@app.route('/requests/three/')
@in_group(("watcher", ))
def requests_three():
    render_ctx = {}
    add_base(render_ctx)
    add_requests_three(render_ctx)
    return render_template('requests_three_report.html', **render_ctx)


@app.route('/requests/four/')
@in_group(("watcher", ))
def requests_four():
    render_ctx = {}
    add_base(render_ctx)
    if 'date' in request.args:
        add_requests_four(render_ctx, request.args['date'])
        return render_template("requests_four_report.html", **render_ctx)
    return render_template('requests_four_form.html', **render_ctx)


@app.route('/batch_form', methods=['GET'])
@in_group(("watcher", "director"))
def batch_form():
    render_ctx = {}
    add_base(render_ctx)
    return render_template('batch_form.html', **render_ctx)


@app.route('/batch_form', methods=['POST'])
@in_group(("watcher", "director"))
def batch_form_post():
    errors = []
    if 'date' in request.form:
        data = request.form['date'].split('-')
        if len(data) == 2:
            year, month = request.form['date'].split('-', 2)
            return redirect(f"/batch_report?month={month}&year={year}")
        else:
            errors.append("Введите дату")
    render_ctx = {}
    add_base(render_ctx)
    render_ctx["errors"] = errors
    return render_template('batch_form.html', **render_ctx)


@app.route("/batch_report")
@in_group(("director", "watcher"))
def batch_report():
    render_ctx = {}
    add_base(render_ctx)
    month = request.args.get("month")
    year = request.args.get("year")
    add_report_batch(render_ctx, month, year)
    return render_template('batch_report.html', **render_ctx)


@app.route('/book_report')
@in_group(("librariest", "watcher"))
def book_report():
    render_ctx = {}
    add_base(render_ctx)
    add_report_book(render_ctx)
    return render_template('book_report.html', **render_ctx)


@app.route('/publishers/<name>')
@in_group(("watcher", ))
def publishers(name):
    render_ctx = {}
    add_base(render_ctx)
    add_books(render_ctx, name)
    return render_template('book_order.html', **render_ctx)


@app.route('/cart')
@in_group(("watcher", ))
def cart():
    render_ctx = {}
    add_base(render_ctx)
    add_cart(render_ctx)
    return render_template("cart.html", **render_ctx)


@app.route('/cart', methods=['PUT', 'POST'])
@in_group(("watcher", ))
def cart_put():
    if 'ed_id' in request.args:
        ed_id = request.args['ed_id']
        count = 1
        if 'count' in request.args:
            try:
                count = int(request.args['count'])
            except ValueError:
                return abort(400)
        if request.method == "PUT":
            put_to_cart(ed_id, count)
        else:
            add_to_cart(ed_id, count)
        return '', 200
    return abort(400)


@app.route('/cart', methods=['DELETE'])
@in_group(("watcher", ))
def cart_del():
    if 'ed_id' in request.args:
        ed_id = request.args['ed_id']
        del_from_cart(ed_id)
        return '', 200
    return abort(400)


@app.route('/order', methods=['POST'])
@in_group(("watcher", ))
def order():
    make_order()
    return '', 200


@app.route('/books', methods=['GET'])
@in_group(("watcher", ))
def books():
    render_ctx = {}
    add_base(render_ctx)
    add_report_book(render_ctx)
    return render_template('books.html', **render_ctx)


@app.route('/books/<int:id>', methods=["GET"])
@in_group(("watcher", ))
def book_edit(id):
    render_ctx = {}
    add_base(render_ctx)
    form = BookForm()
    fill_form(id, form)
    render_ctx['form'] = form
    return render_template("book.html", **render_ctx, method="POST", label="Изменение книжки")


@app.route('/books/<int:id>', methods=["POST"])
@in_group(("watcher", ))
def book_edit_post(id):
    form = BookForm()
    if not form.validate_on_submit():
        render_ctx = {}
        add_base(render_ctx)
        render_ctx['form'] = form
        return render_template("book.html", **render_ctx, method="POST", label="Изменение книжки")
    update_book(id, form)
    return redirect('/books')


@app.route('/books/new', methods=["GET"])
@in_group(("watcher", ))
def book_new():
    render_ctx = {}
    add_base(render_ctx)
    render_ctx['form'] = BookForm()
    return render_template("book.html", **render_ctx, method="POST", url='/books/new', label="Добавление книжки")


@app.route('/books/new', methods=["POST"])
@in_group(("watcher", ))
def book_new_put():
    form = BookForm()
    if not form.validate_on_submit():
        render_ctx = {}
        add_base(render_ctx)
        render_ctx['form'] = form
        return render_template("book.html", **render_ctx, method="POST", url='/books/new', label="Добавление книжки")
    insert_book(form)
    return redirect('/books')


@app.route('/books/<int:id>', methods=['DELETE'])
@in_group(("watcher", ))
def books_delete(id):
    cursor = group_connect().cursor()
    query = "DELETE FROM Library WHERE (`B_id` = %s);"
    cursor.execute(query, (id, ))
    group_connect().commit()
    return '', 200
