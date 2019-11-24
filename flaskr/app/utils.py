from flask import session
from flaskr.db.db import group_connect
from flaskr.auth.checkers import is_logged_in
from flaskr.auth.cart import get_cart, cart_clear


def add_cart(render_ctx):
    shopping_cart = get_cart()
    if len(shopping_cart) < 1:
        return
    render_ctx['cart'] = []
    for book in shopping_cart:
        cursor = group_connect().cursor()
        query = """SELECT title, author_name, genre, one_price 
                FROM edition JOIN book using(b_id)
                Where e_id = %s;"""
        cursor.execute(query, (book,))
        result = cursor.fetchone()
        render_ctx['cart'].append({
            'title': result[0],
            'author': result[1],
            'genre': result[2],
            'cost': result[3],
            'id': book,
            'count': shopping_cart[book]
        })


def make_order():
    cursor = group_connect().cursor()
    s_cart = get_cart()
    publs = {}
    for book in s_cart:
        query = """SELECT ph_id, One_price * %s 
                FROM edition
                Where e_id = %s;"""
        cursor.execute(query, (s_cart[book], book))
        result = cursor.fetchone()
        if result:
            if result[0] not in publs:
                publs[result[0]] = 0
            publs[result[0]] += int(result[1])
    query = """INSERT INTO Batch_of_books (`Bb_date`, `Total_cost`, `Ph_id`)
                VALUES(curdate(), %s, %s)"""
    cursor.executemany(query, [(publs[publ], publ) for publ in publs])
    group_connect().commit()
    query = """
        INSERT INTO Delivery_list 
        (`Numb_of_copies`, `P_year`, `One_price`, `Bb_id`, `B_id`)
        SELECT %s, YEAR(curdate()), one_price, MAX(Bb_id), b_id FROM Edition 
            JOIN batch_of_books USING(Ph_id) 
            WHERE e_id = %s GROUP BY e_id;
    """
    cursor.executemany(query, [(s_cart[book], book) for book in s_cart])
    group_connect().commit()
    cart_clear()


def add_publishers(render_ctx):
    cursor = group_connect().cursor()
    query = "SELECT P_title From publishing_house"
    cursor.execute(query)
    publishers = cursor.fetchall()
    render_ctx['publishers'] = []
    for publ in publishers:
        render_ctx['publishers'].append(*publ)


def add_report_batch(render_ctx, month, year):
    cursor = group_connect().cursor()
    query = """SELECT b.title, b.genre, b.author_name, SUM(d.one_price), SUM(d.Numb_of_copies)
                FROM book as b JOIN delivery_list as d USING (b_id)
                JOIN batch_of_books as bb USING(bb_id)
                WHERE YEAR(bb.Bb_date) = %s AND MONTH(bb.Bb_date) = %s
                GROUP BY b.b_id;"""
    cursor.execute(query, (year, month))
    report = cursor.fetchall()
    render_ctx['report'] = []
    for book in report:
        render_ctx['report'].append(book)


def add_report_book(render_ctx):
    cursor = group_connect().cursor()
    query = """select b.title, b.genre, b.author_name, l.numb_of_copies, l.one_price, b.b_id
                from book as b join library as l using (b_id);"""
    cursor.execute(query)
    report = cursor.fetchall()
    render_ctx['report'] = []
    for book in report:
        render_ctx['report'].append(book)


def add_requests_one(render_ctx, date, book):
    year, month = date.split('-', 2)
    cursor = group_connect().cursor()
    query = """
        SELECT ph.P_title, ph.addres, ph.contact_name, ph.phone, ph.found_year, ph.contract_date
                FROM Publishing_house as ph
                JOIN Batch_of_books as bb USING(Ph_id)
                JOIN Delivery_list as dl USING(Bb_id)
                JOIN Book as b USING(B_id)
                WHERE 
                    YEAR(bb.Bb_date)=%s
                    AND MONTH(bb.Bb_date)=%s
                    AND b.title = %s
                    AND dl.one_price = (
                        SELECT MAX(One_price) FROM Delivery_list
                        JOIN Batch_of_books USING(Bb_id) JOIN Book USING(B_id) 
                            WHERE
                                YEAR(Bb_date)=%s
                                AND MONTH(Bb_date)=%s
                                AND title = %s
                    )
        GROUP BY ph.Ph_id;
    """
    cursor.execute(query, (year, month, book, year, month, book))
    report = cursor.fetchall()
    render_ctx['report'] = []
    for book in report:
        render_ctx['report'].append(book)


def add_requests_two(render_ctx, date, half):
    cursor = group_connect().cursor()
    if half == '1':
        query = """SELECT p_title, addres, contact_name, phone, found_year, contract_date
                    FROM Publishing_house JOIN Batch_of_books USING(Ph_id)
                    WHERE Total_cost=(SELECT MAX(Total_cost) FROM Batch_of_books
                    WHERE YEAR(Bb_date)=%s
                    AND MONTH(Bb_date) < 7)
                    GROUP BY Ph_id;"""
    else:
        query = """SELECT p_title, addres, contact_name, phone, found_year, contract_date
                    FROM Publishing_house JOIN Batch_of_books USING(Ph_id)
                    WHERE Total_cost=(SELECT MAX(Total_cost) FROM Batch_of_books
                    WHERE YEAR(Bb_date)=%s
                    AND MONTH(Bb_date) >= 7) 
                    GROUP BY Ph_id;"""
    cursor.execute(query, (date,))
    report = cursor.fetchall()
    render_ctx['report'] = []
    for book in report:
        render_ctx['report'].append(book)


def add_requests_three(render_ctx):
    cursor = group_connect().cursor()
    query = """SELECT p_title, addres, contact_name, phone, found_year, contract_date 
                FROM Publishing_house LEFT JOIN Batch_of_books USING(Ph_id)
                WHERE Bb_id is NULL;"""
    cursor.execute(query)
    report = cursor.fetchall()
    render_ctx['report'] = []
    for book in report:
        render_ctx['report'].append(book)


def add_requests_four(render_ctx, date):
    year, month = date.split('-', 2)
    cursor = group_connect().cursor()
    query = """SELECT p_title, addres, contact_name, phone, found_year, contract_date 
                FROM Publishing_house LEFT JOIN (SELECT * FROM Batch_of_books
                WHERE YEAR(Bb_date)=%s
                AND MONTH(Bb_date)=%s)ex
                USING(Ph_id)
                WHERE Bb_id is NULL"""
    cursor.execute(query, (year, month))
    report = cursor.fetchall()
    render_ctx['report'] = []
    for book in report:
        render_ctx['report'].append(book)


def add_books(render_ctx, p_title):
    cursor = group_connect().cursor()
    query = """SELECT title, author_name, genre, one_price, e_id 
                FROM edition JOIN book using(b_id) JOIN Publishing_house using(ph_id)
                Where p_title = %s;"""
    cursor.execute(query, (p_title, ))
    report = cursor.fetchall()
    render_ctx['report'] = []
    for book in report:
        render_ctx['report'].append(book)


def add_base(render_ctx):
    if is_logged_in():
        render_ctx['auth'] = True
        render_ctx['login'] = session['login']
        render_ctx['group'] = session['g_log']
    else:
        render_ctx['auth'] = False


group_menu = {
    'librariest':
        {
            'menu':
                [
                    {
                        'img': 'static/img/lib.jpg',
                        'url': '/book_report',
                        'header': 'Просмотр отчетов',
                        'text': 'Просмотр отчетов о книгах в библиотеке'
                    }
                ]
        },
    'watcher':
        {
            'menu':
                [
                    {
                        'img': '/static/img/lib.jpg',
                        'url': '/batch_form',
                        'header': 'Просмотр отчетов',
                        'text': 'Просмотр отчетов о поставке'
                    },
                    {
                        'img': '/static/img/lib.jpg',
                        'url': '/book_report',
                        'header': 'Просмотр отчетов',
                        'text': 'Просмотр отчетов о книгах в библиотеке'
                    },
                    {
                        'img': '/static/img/lib.jpg',
                        'url': '/requests',
                        'header': 'Запросы к БД',
                        'text': 'Выполнение запросов к БД'
                    },
                    {
                        'img': '/static/img/lib.jpg',
                        'url': '/publishers',
                        'header': 'Заказ книг',
                        'text': 'Здесь вы можете заказать книги для библиотеки'
                    },
                    {
                        'img': '/static/img/lib.jpg',
                        'url': '/books',
                        'header': 'Редактирование',
                        'text': 'Редактироване данных о книгах в библиотеке'
                    }
                ]

        },
    'director':
        {
            'menu':
                [
                    {
                        'img': 'static/img/lib.jpg',
                        'url': '/batch_form',
                        'header': 'Просмотр отчетов',
                        'text': 'Просмотр отчетов о поставке'
                    }
                ]

        },
}


def add_group_menu(render_ctx):
    if is_logged_in():
        group = session['g_log']
        if group in group_menu:
            render_ctx.update(group_menu[group])


def fill_form(id, form):
    cursor = group_connect().cursor()
    query = """select b.title, b.genre, b.author_name, l.numb_of_copies, l.one_price
                from book as b join library as l using (b_id);
                where l.l_id = %s"""
    cursor.execute(query, (id, ))
    result = cursor.fetchone()
    form.title.data = result[0]
    form.genre.data = result[1]
    form.author.data = result[2]
    form.count_copies.data = result[3]
    form.price.data = result[4]


def update_book(id, form):
    cursor = group_connect().cursor()
    query = """UPDATE `Book` SET `Author_name`=%s, `Title`=%s, `Genre`=%s 
            WHERE (`B_id` = (SELECT b_id FROM library WHERE l_id=%s));"""
    cursor.execute(query, (form.author.data, form.title.data, form.genre.data, id))
    group_connect().commit()
    query = """UPDATE library.Library SET One_price = %s, Numb_of_copies = %s
            WHERE l_id = %s;"""
    cursor.execute(query, (form.price.data, form.count_copies.data, id))
    group_connect().commit()


def insert_book(form):
    cursor = group_connect().cursor()
    query = """INSERT INTO Book (`Author_name`, `Title`, `Genre`)
                VALUES(%s, %s, %s)"""
    cursor.execute(query, (form.author.data, form.title.data, form.genre.data))
    group_connect().commit()
    id = cursor.lastrowid
    query = """INSERT INTO Library (`One_price`, `Numb_of_copies`, `B_id`)
                VALUES(%s, %s, %s)"""
    cursor.execute(query, (form.price.data, form.count_copies.data, id))
    group_connect().commit()


