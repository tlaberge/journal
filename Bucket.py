from os import path, environ, listdir
import re

import boto3

from Entry import Entry


class Bucket(object):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def get_entries(self):
        raise NotImplemented

    def put_entry(self, entry):
        Entry.is_instance(entry)

    @staticmethod
    def bucket_factory():
        if 'S3_BUCKET' in environ:
            return S3Bucket(environ['S3_BUCKET'])
        elif 'BUCKET_DIR' in environ:
            return DirectoryBucket(environ['BUCKET_DIR'])


class S3Bucket(Bucket):
    def __init__(self, bucket_name):
        Bucket.__init__(self, bucket_name)
        self.s3 = boto3.resource('s3')

    def get_entries(self):
        entries = []
        bucket = self.s3.Bucket(self.bucket_name)
        for key in bucket.objects.all():
            resp = self.s3.Object(self.bucket_name, key.key).get()
            text = resp['Body'].read().decode()
            entries.append(Entry(text, timestamp=key.key))

        return Entry.sort_entries(entries)

    def put_entry(self, entry):
        Bucket.put_entry(self, entry)
        self.s3.Object(self.bucket_name, str(entry.timestamp)).put(Body=entry.text, ServerSideEncryption='AES256')


class DirectoryBucket(Bucket):
    def __init__(self, bucket_name):
        Bucket.__init__(self, bucket_name)

    def get_entries(self):
        # Look for files named like timestamps: e.g., 123.456, where '.456' is optional.
        file_regex = re.compile(r'(\d+(\.\d+)?)$')
        entry_file_names = filter(lambda f: re.search(file_regex, f), listdir(self.bucket_name))
        entries = list()
        for entry_file_name in entry_file_names:
            with open(path.join(self.bucket_name, entry_file_name), 'r') as entry_file:
                entries.append(Entry(entry_file.read(), timestamp=entry_file_name))

        return Entry.sort_entries(entries)

    def put_entry(self, entry):
        Bucket.put_entry(self, entry)
        with open(path.join(self.bucket_name, str(entry.timestamp)), 'w') as entry_file:
            entry_file.write(entry.text)
