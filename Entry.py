from datetime import datetime
from html import escape, unescape
from time import time
from pytz import timezone, utc


class Entry(object):
    user_tz = None

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
        if Entry.user_tz:
            utc_dt = utc.localize(naive_dt)
            local_dt = timezone(Entry.user_tz)
            user_dt = utc_dt.astimezone(local_dt)
        else:
            user_dt = naive_dt
        return "{}<br><br>{}".format(user_dt.strftime("%c"), unescape(self.text))

    @staticmethod
    def sort_entries(entries, since=0):
        filtered_entries = entries
        if since:
            filtered_entries = filter(lambda e: e.timestamp > time() - since, entries)
        return sorted(filtered_entries, key=lambda e: e.timestamp)

    @staticmethod
    def check_attributes(obj):
        if not hasattr(obj, 'text'):
            raise TypeError("Entry object lacks a 'text' attribute")
        if not hasattr(obj, 'timestamp'):
            raise TypeError("Entry object lacks a 'timestamp' attribute")
