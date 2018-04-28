import json
from datetime import datetime
from time import time
from tempfile import NamedTemporaryFile
from os import rename


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

        # Preserve the original file by writing to a temp file and then
        # atomically renaming. If we take an exception, the original file
        # remains. 'delete' is set to False because otherwise the context
        # manager won't be able to unlink the renamed file.
        with NamedTemporaryFile('w', delete=False) as tmp_file:
            json.dump(json_entries, tmp_file)
            rename(tmp_file.name, file_name)
