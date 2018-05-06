from os import path, environ, listdir
import re
import boto3

from Entry import Entry


# A bucket is an abstraction of an append-only list of entries.
# It maintains a write-through cache: The entire back-end is read in at initialization.
# A new entry is appended to the in-memory list and written to the appropriate back-end store.
class Bucket(object):
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.entry_cache = list()

    def get_entries(self, since=0):
        return Entry.sort_entries(self.entry_cache, since)

    def put_entry(self, entry):
        Entry.is_instance(entry)
        self.entry_cache.append(entry)

    @staticmethod
    def bucket_factory(user):
        if 'S3_BUCKET' in environ:
            return S3Bucket("{}.{}".format(environ['S3_BUCKET_BASE'],user))
        elif 'BUCKET_DIR' in environ:
            return DirectoryBucket("{}.{}".format(environ['BUCKET_DIR_BASE'], user))
        else:
            raise ValueError("Need to export S3_BUCKET_BASE or BUCKET_DIR_BASE")


class S3Bucket(Bucket):
    def __init__(self, bucket_name):
        Bucket.__init__(self, bucket_name)
        self.s3 = boto3.resource('s3')
        self.entry_cache = self.get_entries_from_bucket()

    def get_entries_from_bucket(self):
        entries = []
        bucket = self.s3.Bucket(self.bucket_name)
        for key in bucket.objects.all():
            resp = self.s3.Object(self.bucket_name, key.key).get()
            text = resp['Body'].read().decode()
            entry = Entry(text, timestamp=key.key)
            entries.append(entry)

        return Entry.sort_entries(entries)

    def put_entry(self, entry):
        Bucket.put_entry(self, entry)
        self.s3.Object(self.bucket_name, str(entry.timestamp)).put(Body=entry.text, ServerSideEncryption='AES256')


class DirectoryBucket(Bucket):
    def __init__(self, bucket_name):
        Bucket.__init__(self, bucket_name)
        self.entry_cache = self.get_entries_from_bucket()

    def get_entries_from_bucket(self):
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
