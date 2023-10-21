#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import json
import numpy as np

seed = 43
random.seed(seed)
np.random.seed(seed)


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


gen_q_file = "data/spider/full_gen_q.json"
index_file = "data/spider/train.json"
q_per_db = 2
n = 64  # shot

train = read_jsonl(index_file)


db2items = {}
for item in train:
    db2items.setdefault(item['db_id'], [])
    db2items[item['db_id']].append(item)
print(f"train db num: {len(db2items.keys())}")

gen_q = []  # for generating question,
for db, items in db2items.items():
    for i in range(q_per_db):
        ice_ids = np.random.choice(indices, size=n, replace=False).tolist()
        item = items[0].copy()  # keep the db info (e.g., db id, db path etc.)
        random.shuffle(ice_ids)
        item['ctxs'] = ice_ids
        item['question'] = ""
        item['query'] = ""
        gen_q.append(item)

print(f"gen q: {len(gen_q)}")
save_jsonl(gen_q_file, gen_q)
