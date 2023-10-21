#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import os
import json
from datasets import load_dataset
seed = 43
random.seed(seed)
n = 10
m = 200  # generate question file gen_q_file

os.makedirs("data/break", exist_ok=True)
train_json = "data/break/train.json"
dev_json = "data/break/dev.json"
# test_json = "data/break/test.json"
few_shot_file = f"data/break/{n}_shot.json"
dev_few_shot_file = f"data/break/dev_{n}_shot.json"
gen_q_file = f"data/break/{n}_gen_q.json"


def save_jsonl(path, entries):
    with open(path, 'w', encoding='utf8') as fh:
        for entry in entries:
            fh.write(f'{json.dumps(entry)}\n')


def keep_xy(example):
    return {"question_text": example['question_text'], 'decomposition': example['decomposition']}


data = load_dataset("break_data", "QDMR")

train = list(data['train'].map(keep_xy, load_from_cache_file=False, remove_columns=data['train'].column_names))
save_jsonl(train_json, train)

dev = list(data['validation'].map(keep_xy, load_from_cache_file=False, remove_columns=data['validation'].column_names))
random.shuffle(dev)
dev = dev[:1000]
save_jsonl(dev_json, dev)


random.shuffle(train)
items_few = train[:n]
ice_ids = list(range(n))
for item in dev:
    item['ctxs'] = ice_ids


print(f"few-shot: {len(items_few)}; dev: {len(dev)}")
save_jsonl(few_shot_file, items_few)
save_jsonl(dev_few_shot_file, dev)


datas = []
for i in range(m):
    ice_ids = list(range(n))
    random.shuffle(ice_ids)
    data = {"question_text": "", "decomposition": "", "ctxs": ice_ids}
    datas.append(data)

save_jsonl(gen_q_file, datas)