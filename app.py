# coding=utf-8
import os
import flask as f
import sqlalchemy as db
import flask_bootstrap as fb


engine = db.create_engine('sqlite:///database.sqlite')
app = f.Flask('py_vulnerable_site')
fb.Bootstrap(app)


def query(text):
    conn = engine.connect()
    res = conn.execute(text)
    res = res.fetchall()
    return res


@app.route('/', methods=['GET'])
def get_index():
    return f.render_template('index.html')


@app.route('/about', methods=['GET'])
def get_about():
    files = os.listdir('./static/legal/')
    doc = f.request.args.get('doc')
    if doc:
        doc = open(doc).read()
    else:
        doc = 'Selecione um arquivo para ler nos links acima.'
    return f.render_template('about.html', files=files, doc=doc)


@app.route('/contact', methods=['GET'])
def get_contact():
    return f.render_template('contact.html')


@app.route('/signup', methods=['GET'])
def get_signup():
    return f.render_template('signup.html')


@app.route('/login', methods=['GET'])
def get_login():
    return f.render_template('/login.html', msg='')


@app.route('/login', methods=['POST'])
def post_login():
    lg = f.request.form['login'] or 'blank'
    pw = f.request.form['senha'] or 'blank'
    q = f'select type from logins where login = "{lg}" and password = "{pw}"'
    res = query(q)
    if len(res) == 0:
        return f.render_template('/login.html', msg='Login incorreto!')
    else:
        res = res[0][0]
        redirect = f.redirect('/restrict')
        r = f.make_response(redirect)
        r.set_cookie('pyverysafelogin', value=res)
        return r


@app.route('/restrict', methods=['GET'])
def get_restrict():
    cookie = f.request.cookies.get('pyverysafelogin')
    if cookie:
        q = f'SELECT info FROM info WHERE level LIKE "%{cookie}%"'
        res = query(q)
        return f.render_template('restrict.html', level=cookie, info=res)
    else:
        return f.redirect('/login')


@app.route('/logout', methods=['GET'])
def get_logout():
    redirect = f.redirect('/login')
    r = f.make_response(redirect)
    r.set_cookie('pyverysafelogin', '', expires=0)
    return r


@app.route('/search', methods=['GET'])
def get_search():
    search = f.request.args.get('text')
    search = f'SELECT * FROM posts WHERE Content LIKE "%{search}%";'
    res = query(search)
    if len(res) == 0:
        res = [('Que Pena!', 'Sua pesquisa não retornou resultados. \
                Tenta outra coisa :D')]
    return f.render_template('search.html', items=res)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)