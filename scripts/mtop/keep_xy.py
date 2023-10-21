import json
import sys

path = sys.argv[1]


def save_jsonl(path, entries):
    with open(path, 'w', encoding='utf8') as fh:
        for entry in entries:
            fh.write(f'{json.dumps(entry)}\n')


def read_jsonl(path):
    pairs = []
    with open(path, 'r', encoding='utf8') as fh:
        for line in fh:
            pairs.append(json.loads(line))
    return pairs


def keep_xy(example):
    return {"question": example['question'], 'logical_form': example['logical_form']}


data = read_jsonl(path)

data = [keep_xy(i) for i in data]
save_jsonl(path, data)
