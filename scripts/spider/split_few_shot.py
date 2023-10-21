#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import random
from datasets import load_dataset
import os
import sys
sys.path.append(".")

seed = 43
random.seed(seed)
n = 10
# random q_per_db ctxs to form few shots for generating question
# for 140 dbs, total number of prompts for generating question is 2*144=288
q_per_db = 2

os.makedirs("data/spider", exist_ok=True)
train_json = "data/spider/train.json"
dev_json = "data/spider/dev.json"
few_shot_file = f"data/spider/{n}_shot.json"
dev_few_shot_file = f"data/spider/dev_{n}_shot.json"
gen_q_file = f"data/spider/{n}_gen_q.json"


def save_jsonl(path, entries):
    with open(path, 'w', encoding='utf8') as fh:
        for entry in entries:
            fh.write(f'{json.dumps(entry)}\n')


data = load_dataset("src/dataset/spider.py", "spider")

train = list(data['train'])
save_jsonl(train_json, train)

dev = list(data['validation'])
save_jsonl(dev_json, dev)


db2items = {}
for item in train:
    db2items.setdefault(item['db_id'], [])
    db2items[item['db_id']].append(item)
print(f"train db num: {len(db2items.keys())}")

random.shuffle(train)
items_few = train[:n]
ice_ids = list(range(n))
for item in dev:
    item['ctxs'] = ice_ids

save_jsonl(few_shot_file, items_few)
save_jsonl(dev_few_shot_file, dev)


gen_q = []  # for generating question,
for db, items in db2items.items():
    for i in range(q_per_db):
        ice_ids = ice_ids.copy()
        item = items[0].copy()  # keep the db info (e.g., db id, db path etc.)
        random.shuffle(ice_ids)
        item['ctxs'] = ice_ids
        item['question'] = ""
        item['query'] = ""
        gen_q.append(item)

print(f"all: {len(dev)}; few-shot: {len(items_few)}; gen q: {len(gen_q)}")
save_jsonl(gen_q_file, gen_q)