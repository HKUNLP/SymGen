#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import os
import json
seed = 43
random.seed(seed)
n = 10
m = 1000  # generate question file gen_q_file

task = 'geoquery'
os.makedirs(f"data/{task}", exist_ok=True)
train_json = f"data/{task}/train.json"
dev_json = f"data/{task}/dev.json"
few_shot_file = f"data/{task}/{n}_shot.json"
dev_few_shot_file = f"data/{task}/dev_{n}_shot.json"
gen_q_file = f"data/{task}/{n}_gen_q.json"


def read_csv(split):
    with open(f"data/geoquery/{split}.csv") as f1:
        data = [{'nl': l.strip().split('\t')[0], 'prolog': l.strip().split('\t')[1]} for l in f1.readlines()]
        data = sorted(data, key=lambda x: x['nl'])
    return data


def save_jsonl(path, entries):
    with open(path, 'w', encoding='utf8') as fh:
        for entry in entries:
            fh.write(f'{json.dumps(entry)}\n')


train = read_csv('train')
dev = read_csv('dev')
save_jsonl(train_json, train)
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
    data = {"nl": "", "prolog": "", "ctxs": ice_ids}
    datas.append(data)

save_jsonl(gen_q_file, datas)