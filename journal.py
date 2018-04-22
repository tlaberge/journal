from flask import Flask, render_template, request
from argparse import ArgumentParser
app = Flask(__name__)


@app.route('/', methods=['get', 'post'])
def index():
    entries = ["First entry", "It was a dark and stormy night."]
    return render_template('journal.j2', entries=entries)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    args = parser.parse_args()

    app.run(debug=args.debug)
