#!/usr/bin/python3
# -*- coding: utf-8 -*-
import random
import json

seed = 43
random.seed(seed)


def save_json(file, data_list):
    with open(file, 'w', encoding='utf8') as fh:
        fh.write(f'{json.dumps(data_list)}')


gen_q_file = "data/nl2bash/few_gen_q.json"
m = 200
n = 10  # shot

datas = []
for i in range(m):
    ice_ids = list(range(n))
    random.shuffle(ice_ids)
    data = {"nl": "", "bash": "", "ctxs": ice_ids}
    datas.append(data)

save_json(gen_q_file, datas)
