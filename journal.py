from argparse import ArgumentParser
from flask import Flask, render_template, request
from os import environ

from Entry import Entry

entry_file = None
bucket_name = None
user = None

app = Flask(__name__)


@app.route('/', methods=['get', 'post'])
def index():
    if request.method == 'POST':
        print(request.form.get('Entry'))
        entry = Entry(request.form.get('Entry'))

        if entry_file:
            entries = Entry.entries_from_json_file(entry_file)
            entries.append(entry)
            Entry.entries_to_json_file(entry_file, entries)
        else:
            Entry.push_entry_to_s3(bucket_name, entry)

    if entry_file:
        entries = Entry.entries_from_json_file(entry_file)
    else:
        entries = Entry.get_entries_from_s3(bucket_name)

    return render_template('journal.j2', user=user, entries=sorted(entries, key=lambda e: e.timestamp))


def main():
    global entry_file
    global bucket_name
    global user

    if 'ENTRY_FILE' in environ:
        entry_file = environ['ENTRY_FILE']
    elif 'S3_BUCKET' in environ:
        bucket_name = environ['S3_BUCKET']
    else:
        raise ValueError("Need ENTRY_FILE or S3_BUCKET in environment")

    parser = ArgumentParser()
    parser.add_argument('--debug', '-d', action='store_true', default=False)
    parser.add_argument('--user', '-u', action='store', default="Tim")
    args = parser.parse_args()

    user = args.user
    app.run(debug=args.debug)


if __name__ == "__main__":
    main()
