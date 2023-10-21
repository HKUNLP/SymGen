#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import os
import json
seed = 43
random.seed(seed)
n = 10

os.makedirs("data/nl2bash", exist_ok=True)
train_json = "data/nl2bash/train.json"
dev_json = "data/nl2bash/dev.json"
test_json = "data/nl2bash/test.json"
few_shot_file = "data/nl2bash/few_shot.json"
test_few_shot_file = "data/nl2bash/test_few_shot.json"

root_dir = "third_party/nl2bash/data/bash/"


def read_merge(spilt):
    with open(root_dir+f"{spilt}.nl.filtered") as f1, open(root_dir+f"{spilt}.cm.filtered") as f2:
        nl = [l.strip() for l in f1.readlines()]
        cm = [l.strip() for l in f2.readlines()]
        data = []
        for i, j in zip(nl, cm):
            data.append({'nl': i, 'bash': j})
    return data


def save_jsonl(path, entries):
    with open(path, 'w', encoding='utf8') as fh:
        for entry in entries:
            fh.write(f'{json.dumps(entry)}\n')


train = read_merge('train')
dev = read_merge('dev')
test = read_merge('test')
save_jsonl(train_json, train)
save_jsonl(dev_json, dev)
save_jsonl(test_json, test)

random.shuffle(train)
items_few = train[:n]
ice_ids = list(range(n))
for item in test:
    item['ctxs'] = ice_ids


print(f"few-shot: {len(items_few)}; test: {len(test)}")
save_jsonl(few_shot_file, items_few)
save_jsonl(test_few_shot_file, test)


