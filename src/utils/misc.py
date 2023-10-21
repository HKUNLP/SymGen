#!/usr/bin/python3
# -*- coding: utf-8 -*-

from multiprocessing import Pool, TimeoutError
from tqdm import tqdm
from functools import partial
import json
import logging
from copy import deepcopy


logger = logging.getLogger(__name__)


class App:
    def __init__(self, dict_funcs=None):
        self.functions = {}
        if dict_funcs is not None:
            self.functions.update(dict_funcs)

    def add(self, key):
        def adder(func):
            self.functions[key] = func
            return func

        return adder

    def __getitem__(self, __name: str):
        return self.functions[__name]

    def merge(self, app):
        new_app = App()
        new_app.functions = self.functions.update(app.functions)
        return new_app


class SafeFormatDict(dict):
    def __missing__(self, key):
        return '{' + key + '}'


def save_format(text, **kwargs):
    return text.format_map(SafeFormatDict(**kwargs))


def wrapper(idx_args, func):
    idx, args = idx_args
    res = func(args)
    return idx, res


def parallel_run(func, args_list, n_processes=8, initializer=None, **kwargs):
    idx2res = {}
    func = partial(func, **kwargs)
    n = len(args_list)
    with Pool(n_processes, initializer=initializer) as p:
        for idx, response in tqdm(p.imap_unordered(partial(wrapper, func=func),
                                                   enumerate(args_list)),
                                  total=n):
            idx2res[idx] = response

    res = [idx2res[i] for i in range(n)]
    return res


def parallel_run_timeout(func, args_list, n_processes=8, timeout=5, **kwargs):
    pool = Pool(n_processes)
    jobs = {}
    results = []
    restart = False

    for i, args in enumerate(args_list):
        jobs[i] = pool.apply_async(func, args=(args, ), kwds=kwargs)

    total_num = len(args_list)
    finished_num = 0
    fail_num = 0
    for i, r in tqdm(jobs.items()):
        try:
            finished_num += 1
            results.append(r.get(timeout=timeout))
        except TimeoutError as e:
            results.append(('exception', TimeoutError))
            logger.info("Timeout args: ")
            logger.info(args_list[i])
            fail_num += 1
            if fail_num == n_processes and total_num > finished_num:
                restart = True
                logger.info(f"All processes down, restart, remain {total_num-finished_num}/{total_num}")
                break

    pool.close()
    pool.terminate()
    pool.join()

    if restart:
        results.extend(parallel_run_timeout(func, args_list[finished_num:], n_processes, timeout, **kwargs))
    return results


def save_json(file, data_list):
    logger.info(f"Saving to {file}")
    with open(file, "w") as f:
        json.dump(data_list, f)


def load_json(file):
    logger.info(f"Loading from {file}")
    with open(file) as f:
        data = json.load(f)
    return data


def save_jsonl(path, entries):
    logger.info(f"Saving to {path}")
    with open(path, 'w', encoding='utf8') as fh:
        for entry in entries:
            fh.write(f'{json.dumps(entry)}\n')


def read_jsonl(path):
    pairs = []
    logger.info(f"Loading from {path}")
    with open(path, 'r', encoding='utf8') as fh:
        for line in fh:
            pairs.append(json.loads(line))
    return pairs


def flatten_entries(entries, return_index=False):
    # convert entry with multiple candidates to list of entries
    flattened = []
    indices = []
    cand_fields = list(entries[0]['candidates'][0].keys())
    for idx, entry in enumerate(entries):
        candidates = entry.pop("candidates")
        for candidate in candidates:
            example = deepcopy(entry)
            example.update(candidate)
            flattened.append(example)
            indices.append(idx)

    if return_index:
        return flattened, indices, cand_fields
    else:
        return flattened


def pack_entries_by_indices(flattened_entries, indices, cand_fields):
    # inverse process of above function
    idx2entries = {}
    for idx, entry in zip(indices, flattened_entries):
        cand = {k: entry.pop(k) for k in cand_fields}
        if idx not in idx2entries:
            entry['candidates'] = [cand]
            entry = deepcopy(entry)
            idx2entries[idx] = entry
        else:
            idx2entries[idx]['candidates'].append(cand)
    sorted_keys = sorted(idx2entries)

    entries = []
    for k in sorted_keys:
        entries.append(idx2entries[k])
    return entries
