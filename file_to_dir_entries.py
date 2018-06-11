
from argparse import ArgumentParser
from time import mktime, strptime
from Entry import Entry
from Bucket import Bucket


parser = ArgumentParser()
parser.add_argument('--user', action='store', required=True)
parser.add_argument('--input_file', action='store', required=True)
args = parser.parse_args()

bucket = Bucket.bucket_factory(args.user)

with open(args.input_file, 'r') as input_file:
    file_content = input_file.read()

chunks = file_content.split('-' * 80)
for chunk in chunks:
    lines = chunk.split('\n')
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()

    if not lines:
        continue

    struct_time = strptime(lines[0])
    timestamp = mktime(struct_time)

    text = '\n'.join(lines[2:])

    entry = Entry(text, timestamp)
    bucket.put_entry(entry)