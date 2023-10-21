#!/usr/bin/python3
# -*- coding: utf-8 -*-
from src.utils.misc import parallel_run, parallel_run_timeout
from src.filters.filter_tool import *
from src.utils.spider.sql_util import *


def _a_post_process(entry):
    for i, res_dict in enumerate(entry['candidates']):
        res_dict['query'] = sql_process(res_dict['text'])
        res_dict.pop('text')
    return entry


def by_a_post_process(entries):
    return parallel_run(_a_post_process, entries)


filter_getter = {
    'gen_a': {'post_proc': by_a_post_process,
              'dedup': partial(by_dedup, field='query'),
              'exec': partial(by_exec, func=exec_on_db),
              'majority_vote': partial(by_majority_vote, check_equal_func=result_eq),
              'argmax': by_max_logprob},
    'gen_q': {'post_proc': partial(text_to_field, field='question'),
              'length': partial(by_length, field='question'),
              'dedup': partial(by_dedup, field='question')}
}
