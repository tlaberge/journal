import json
from datetime import datetime
from time import time
from tempfile import NamedTemporaryFile
from os import rename
from html import escape, unescape

import boto3


class Entry(object):
    s3 = boto3.resource('s3')

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

    def to_json_dict(self):
        return {'text': self.text, 'timestamp': str(self.timestamp)}

    def __str__(self):
        return "{}<br><br>{}".format(datetime.fromtimestamp(self.timestamp).strftime("%c"), unescape(self.text))

    @staticmethod
    def from_json_dict(json_dict):
        return Entry(json_dict['text'], float(json_dict['timestamp']))

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

    @classmethod
    def get_entries_from_s3(cls, bucket_name):
        entries = []
        bucket = cls.s3.Bucket(bucket_name)
        for key in bucket.objects.all():
            resp = cls.s3.Object(bucket_name, key.key).get()
            text = resp['Body'].read().decode()
            entries.append(Entry(text, timestamp=key.key))

        return entries

    @classmethod
    def push_entry_to_s3(cls, bucket_name, entry):
        cls.s3.Object(bucket_name, str(entry.timestamp)).put(Body=entry.text, ServerSideEncryption='AES256')
