from flask import Flask, render_template, request
from flask_httpauth import HTTPBasicAuth
from User import User
auth = HTTPBasicAuth()

from os import environ

from Entry import Entry
from Bucket import Bucket

journal_user = "Tim"
subject = ""
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
    bucket = Bucket.bucket_factory()

    if request.method == 'POST':
        entry = Entry(request.form.get('Entry'))
        bucket.put_entry(entry)

    entries = bucket.get_entries()

    return render_template('journal.j2', user=journal_user, subject=subject, entries=entries)


def main():
    global journal_user
    global subject

    if 'BUCKET_DIR' not in environ and 'S3_BUCKET' not in environ:
        raise ValueError("Need BUCKET_DIR or S3_BUCKET in environment")

    if 'JOURNAL_USER' in environ:
        journal_user = environ['JOURNAL_USER']

    if 'JOURNAL_SUBJECT' in environ:
        subject = environ['JOURNAL_SUBJECT']

    port=5000
    if 'PORT' in environ:
        port = int(environ['PORT'])

    debug = False
    if 'DEBUG' in environ:
        debug = True

    app.run(debug=debug, port=port)


if __name__ == "__main__":
    main()
