from datetime import datetime
from html import escape, unescape
from time import time
from pytz import timezone, utc

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
        naive_dt = datetime.fromtimestamp(self.timestamp)
        utc_dt = utc.localize(naive_dt)
        user_tz = timezone('America/Los_Angeles')
        user_dt = utc_dt.astimezone(user_tz)
        return "{}<br><br>{}".format(user_dt.strftime("%c"), unescape(self.text))

    @staticmethod
    def sort_entries(entries, since=0):
        filtered_entries = entries
        if since:
            filtered_entries = filter(lambda e: e.timestamp > time() - since, entries)
        return sorted(filtered_entries, key=lambda e: e.timestamp)

    @staticmethod
    def is_instance(obj):
        if not isinstance(obj, Entry):
            raise TypeError("Entry {} is of type {} require {}".format(obj, type(obj), type(Entry)))
