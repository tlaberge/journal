from collections import OrderedDict
from flask import Flask, render_template, request, session, flash, redirect, url_for
from flask_httpauth import HTTPBasicAuth
import logging
from os import environ, urandom

from Bucket import Bucket
from Entry import Entry

from User import User

auth = HTTPBasicAuth()
user_buckets = dict()
journal_users = dict()
password_file = ".passwords"
port = 5000

app = Flask(__name__)


@auth.verify_password
def verify_password(username, password):
    users = User.users_from_password_file('.passwords')
    if username not in users:
        return False
    user = users[username]
    return user.verify_password(password)


@app.route('/login', methods=['POST'])
def do_admin_login():
    if verify_password(request.form['username'], request.form['password']):
        session['logged_in'] = True
        session['username'] = request.form['username']
    else:
        flash('wrong password!')
    return redirect(url_for('index', _anchor="Entry"))


@app.route('/', methods=['get', 'post'])
def index():
    if not session.get('logged_in'):
        return render_template('login.j2')
    else:
        return journal()


def journal():
    if not session.get('logged_in'):
        flash('Not logged in')

    user = session.get('username')
    bucket = user_buckets[user]

    checked_keys = ['day', 'week', 'month', 'year', 'all']
    checked = OrderedDict()
    for key in checked_keys:
        checked[key] = ''

    since = 0
    if request.method == 'GET':
        checked['all'] = 'checked'
    elif request.method == 'POST':
        form_entry = request.form.get('Entry')
        if form_entry:
            entry = Entry(request.form.get('Entry'))
            bucket.put_entry(entry)

        playback = request.form.get('playback')
        if playback == 'day':
            since = 24 * 3600.0
        elif playback == 'week':
            since = 24 * 3600 * 7.0
        elif playback == 'month':
            since = 24 * 3600 * 31.0
        elif playback == 'year':
            since = 24 * 3600 * 365.25
        elif playback == 'all':
            since = 0

        checked[playback] = 'checked'

    entries = bucket.get_entries(since=since)

    return render_template('journal.j2',
                           user=journal_users[user].display_name,
                           subject=journal_users[user].subject,
                           entries=entries,
                           checked=checked)


def main():
    global password_file
    global journal_users
    global port

    logging.basicConfig(level=logging.INFO)
    if 'BUCKET_DIR_BASE' not in environ and 'S3_BUCKET_BASE' not in environ:
        raise ValueError("Need BUCKET_DIR_BASE or S3_BUCKET_BASE in environment")

    if 'USER_TZ' in environ:
        # Running in AWS, so need to account for TZ.
        Entry.user_tz = environ['USER_TZ']

    if 'PASSWORD_FILE' in environ:
        password_file = environ['PASSWORD_FILE']

    port = 5000
    if 'PORT' in environ:
        port = int(environ['PORT'])
        logging.info("Set port to {}".format(port))

    debug = False
    if 'DEBUG' in environ:
        debug = True

    journal_users = User.users_from_password_file(password_file)
    for user in journal_users:
        user_buckets[user] = Bucket.bucket_factory(user)

    app.secret_key = urandom(12)
    app.run(debug=debug, port=port)


if __name__ == "__main__":
    main()
