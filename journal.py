from flask import Flask, render_template, request
from argparse import ArgumentParser
from os import environ

from Entry import Entry

app = Flask(__name__)

entries = [ Entry("A sample entry")]
entry_file = None
s3_token = None


@app.route('/', methods=['get', 'post'])
def index():
    if entry_file:
        entries = Entry.entries_from_json_file(entry_file)
    else:
        entries = []

    if request.method == 'POST':
        entry = Entry(request.form.get('Entry'))
        entries.append(entry)

        if entry_file:
            Entry.entries_to_json_file(entry_file, entries)

    return render_template('journal.j2', entries=sorted(entries, key=lambda e: e.timestamp))


def main():
    global entry_file
    global s3_token

    if 'ENTRY_FILE' in environ:
        entry_file = environ['ENTRY_FILE']
    elif 'S3_TOKEN' in environ:
        s3_token = environ['S3_TOKEN']
    else:
        raise ValueError("Need ENTRY_FILE or S3_TOKEN in environment")

    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    args = parser.parse_args()

    app.run(debug=args.debug)


if __name__ == "__main__":
    main()