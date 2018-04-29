from flask import Flask, render_template, request
from os import environ

from Entry import Entry
from Bucket import Bucket

user = "Tim"
subject = ""
app = Flask(__name__)


@app.route('/', methods=['get', 'post'])
def index():
    bucket = Bucket.bucket_factory()

    if request.method == 'POST':
        entry = Entry(request.form.get('Entry'))
        bucket.put_entry(entry)

    entries = bucket.get_entries()

    return render_template('journal.j2', user=user, subject=subject, entries=entries)


def main():
    global user
    global subject

    if 'BUCKET_DIR' not in environ and 'S3_BUCKET' not in environ:
        raise ValueError("Need BUCKET_DIR or S3_BUCKET in environment")

    if 'JOURNAL_USER' in environ:
        user = environ['JOURNAL_USER']

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
