#!/usr/bin/python3
# -*- coding: utf-8 -*-
import numpy as np
from itertools import groupby
from torch.utils.data import BatchSampler
from src.utils.misc import *

logger = logging.getLogger(__name__)


def text_to_field(entries, field):
    for entry in entries:
        for i, res_dict in enumerate(entry['candidates']):
            res_dict[field] = res_dict['text']
            res_dict.pop('text')
    return entries


def by_dedup(entries, field):
    """ Keep the largest logprob when duplicate"""
    for entry in entries:
        candidates = entry['candidates']
        candidates = [{field: key, 'logprob': max(item['logprob'] for item in values)}
                      for key, values in groupby(candidates, lambda dct: dct[field])]
        entry['candidates'] = candidates
    return entries


def by_length(entries, field, min_len=5, max_len=40):
    """ Keep the largest logprob when duplicate"""
    for entry in entries:
        entry['candidates'] = list(filter(lambda dct: min_len < len(dct[field].split()) < max_len,
                                          entry['candidates']))
    return entries


def by_max_logprob(entries):
    for entry in entries:
        max_idx = np.array([item['logprob'] for item in entry['candidates']]).argmax()
        entry['candidates'] = [entry['candidates'][max_idx]]
    return entries


def by_exec(entries, func, n_processes=8, timeout=5, batch_size=1, at_least_one=False):
    # make sure func output a tuple, the first element is 'result' if it can execute
    flattened_entries, indices, cand_fields = flatten_entries(entries, return_index=True)

    if batch_size > 1:
        sampler_indices = list(range(len(flattened_entries)))
        sampler = BatchSampler(sampler_indices, drop_last=False, batch_size=batch_size)
        batch_entries = [[flattened_entries[i] for i in batch] for batch in list(sampler)]
        # timeout is set to None as we cannot decide which one cause the timeout in the batch
        batch_results = parallel_run_timeout(func, batch_entries, n_processes=n_processes, timeout=None)
        results = []
        for res in batch_results:
            results.extend(res)
    else:
        results = parallel_run_timeout(func, flattened_entries, n_processes=n_processes, timeout=timeout)

    for res, entry in zip(results, flattened_entries):
        entry['result'] = res

    cand_fields.append('result')
    entries = pack_entries_by_indices(flattened_entries, indices, cand_fields)

    # filter non-executable queries
    kept_queries = []
    for entry in entries:
        candidates = [cand for cand in entry['candidates'] if cand['result'][0] == 'result']
        if len(candidates) == 0:
            if at_least_one:
                max_idx = np.argmax([cand['logprob'] for cand in entry['candidates']])
                # overwrite the error object with None, so that the example can be saved
                # entry['candidates'][max_idx]['result'][1] = None
                candidates = [entry['candidates'][max_idx]]
            else:
                # we only keep those candidates that can execute
                continue
        entry['candidates'] = candidates
        kept_queries.append(entry)
    return kept_queries


def _vote_single(entry, check_equal_func, min_votes, filter_entry=False):
    candidates = entry['candidates']
    num = len(candidates)
    if num > 1:
        eq_matrix = [[0 for _ in range(num)] for _ in range(num)]
        for i in range(num):
            for j in range(i + 1, num):
                assert 'result' in candidates[0], "include exec to filters first"
                if candidates[i]['result'][0] == 'result' and candidates[j]['result'][0] == 'result':
                    eq_matrix[i][j] = check_equal_func(candidates[i]['result'][1], candidates[j]['result'][1])
                else:
                    eq_matrix[i][j] = 0

        eq_matrix = np.array(eq_matrix, dtype=float)
        eq_matrix = eq_matrix + eq_matrix.T + np.identity(num, dtype=float)
        same_votes_num = eq_matrix.sum(-1)

        # keep the queries in the largest cluster(s)
        max_vote = same_votes_num.max()
        min_votes = min_votes if min_votes >= 1 else min_votes * num
        if max_vote >= min_votes:
            # at least min_votes% or min_votes sqls have same results
            keep_query = same_votes_num == max_vote
            entry['candidates'] = [entry['candidates'][i] for i in range(num) if keep_query[i]]
        elif filter_entry:
            # ignore this question as the queries are not consistent
            return None
        else:
            # we keep all queries as we cannot figure out a proper subset
            pass
    return entry


def by_majority_vote(entries, check_equal_func, **kwargs):
    entries_or_none = parallel_run(partial(_vote_single,
                                           check_equal_func=check_equal_func,
                                           **kwargs)
                                   , entries)
    entries = [entry for entry in entries_or_none if entry is not None]
    return entries


def entries_info(entries):
    n = len(entries)
    total_cands = sum([len(entry['candidates']) for entry in entries])
    return {"num_entries": n, "num_candidates": total_cands, "avg_candidates": total_cands / n}


class FilterTool:

    def __init__(self, filter_getter, field, filter_kwargs):
        self.funcs = []
        self.filter_getter = filter_getter
        for filter_func in filter_kwargs:
            func_name = list(filter_func.keys())[0]
            func_kwargs = filter_func[func_name] if filter_func[func_name] is not None else {}
            self.funcs.append((func_name,
                               partial(self.filter_getter[field][func_name],
                                       **func_kwargs)))

    def run(self, entries):
        logger.info(f"Initial: {str(entries_info(entries))}")
        for func_name, func in self.funcs:
            entries = func(entries)
            logger.info(f"After {func_name}: {str(entries_info(entries))}")
        return entries
