import json
from datetime import datetime
from time import time


class Entry(object):
    def __init__(self, text, timestamp=None):
        """
        'text' is the entry's text. It will be formatted as <pre>entry</pre>, so escape >, <, etc.
        'timestamp' is the seconds since the epoch, e.g., as returned by time.time()
        """
        self.text = text
        if timestamp:
            self.timestamp = timestamp
        else:
            self.timestamp = time()

    def to_json_dict(self):
        return {'text': self.text, 'timestamp': self.timestamp}

    def __str__(self):
        return "{}<br><br>{}".format(datetime.fromtimestamp(self.timestamp).strftime("%c"), self.text)

    @staticmethod
    def from_json_dict(json_dict):
        return Entry(json_dict['text'], json_dict['timestamp'])

    @staticmethod
    def entries_from_json_file(file_name):
        entries = []
        with open(file_name, 'r') as json_file:
            json_entries = json.load(json_file)
            for json_dict in json_entries:
                entries.append(Entry.from_json_dict(json_dict))
        return entries

    @staticmethod
    def entries_to_json_file(file_name, entries):
        json_entries = []
        for entry in entries:
            json_entries.append(Entry.to_json_dict(entry))

        with open(file_name, 'w') as json_file:
            json.dump(json_entries, json_file)
