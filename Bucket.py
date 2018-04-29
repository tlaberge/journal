from os import path, environ, chdir, listdir
import re

import boto3

from Entry import Entry


class Bucket(object):
    def __init__(self):
        raise NotImplemented

    def get_entries(self):
        raise NotImplemented

    def put_entry(self):
        raise NotImplemented

    @staticmethod
    def bucket_factory():
        if 'S3_BUCKET' in environ:
            return S3Bucket(environ['S3_BUCKET'])
        elif 'BUCKET_DIR' in environ:
            return DirectoryBucket(environ['BUCKET_DIR'])


class S3Bucket(Bucket):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
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
        if not isinstance(entry, Entry):
            raise TypeError("Entry {} is of type {} require {}".format(entry, type(entry), type(Entry)))

        self.s3.Object(self.bucket_name, str(entry.timestamp)).put(Body=entry.text, ServerSideEncryption='AES256')


class DirectoryBucket(Bucket):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

    def get_entries(self):
        file_regex = re.compile(r'^\d+(\.\d+)*$')
        entries = list()
        chdir(self.bucket_name)
        entry_file_names = filter(lambda f: re.match(file_regex, f), listdir('.'))
        for entry_file_name in entry_file_names:
            with open(entry_file_name, 'r') as entry_file:
                entries.append(Entry(entry_file.read(), timestamp=float(entry_file_name)))

        return Entry.sort_entries(entries)

    def put_entry(self, entry):
        if not isinstance(entry, Entry):
            raise TypeError("Entry {} is of type {} require {}".format(entry, type(entry), type(Entry)))

        with open(path.join(self.bucket_name, str(entry.timestamp)), 'w') as entry_file:
            entry_file.write(entry.text)