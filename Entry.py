from datetime import datetime
from html import escape, unescape
from time import time


class Entry(object):
    def __init__(self, text, timestamp=None):
        """
        'text' is the entry's text. Escape it so that we can use <,&, ; etc in the journal.
        'timestamp' is the seconds since the epoch, e.g., as returned by time.time()
        """
        self.text = escape(text)
        if timestamp:
            self.timestamp = float(timestamp)
        else:
            self.timestamp = time()

    def __str__(self):
        return "{}<br><br>{}".format(datetime.fromtimestamp(self.timestamp).strftime("%c"), unescape(self.text))

    @staticmethod
    def sort_entries(entries):
        return sorted(entries, key=lambda e: e.timestamp)

    @staticmethod
    def is_instance(obj):
        if not isinstance(obj, Entry):
            raise TypeError("Entry {} is of type {} require {}".format(obj, type(obj), type(Entry)))
