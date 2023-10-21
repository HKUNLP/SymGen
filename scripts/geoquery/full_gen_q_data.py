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


gen_q_file = "data/geoquery/full_gen_q.json"
index_file = "data/geoquery/train.json"
m = 1000
n = 64  # shot
indices = list(range(len(read_jsonl(index_file))))

datas = []
for i in range(m):
    ice_ids = np.random.choice(indices, size=n, replace=False).tolist()
    data = {"nl": "", "prolog": "", "ctxs": ice_ids}
    datas.append(data)

print(len(datas))
save_jsonl(gen_q_file, datas)
