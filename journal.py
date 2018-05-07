from collections import OrderedDict
from flask import Flask, render_template, request
from flask_httpauth import HTTPBasicAuth
from os import environ

from Bucket import Bucket
from Entry import Entry

from User import User

auth = HTTPBasicAuth()
user_buckets = dict()
journal_users = dict()
password_file = ".passwords"

app = Flask(__name__)


@auth.verify_password
def verify_password(username, password):
    users = User.users_from_password_file('.passwords')
    if username not in users:
        return False
    user = users[username]
    return user.verify_password(password)


# TODO: Wrap the login_required wrapper so that it's 'login_required if secure' or something...
@app.route('/', methods=['get', 'post'])
@auth.login_required
def index():
    user = request.authorization.username
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

    if 'BUCKET_DIR_BASE' not in environ and 'S3_BUCKET_BASE' not in environ:
        raise ValueError("Need BUCKET_DIR_BASE or S3_BUCKET_BASE in environment")

    if 'PASSWORD_FILE' in environ:
        password_file = environ['PASSWORD_FILE']

    port = 5000
    if 'PORT' in environ:
        port = int(environ['PORT'])

    debug = False
    if 'DEBUG' in environ:
        debug = True

    journal_users = User.users_from_password_file(password_file)
    for user in journal_users:
        user_buckets[user] = Bucket.bucket_factory(user)

    app.run(debug=debug, port=port)


if __name__ == "__main__":
    main()
