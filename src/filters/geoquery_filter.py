#!/usr/bin/python3
# -*- coding: utf-8 -*-
from src.filters.filter_tool import *
from src.metrics.geoquery.prolog_eval import get_denotation


def _a_post_process(entry):
    for i, res_dict in enumerate(entry['candidates']):
        res_dict['prolog'] = "answer(" + res_dict['text']
        # Balance parentheses
        num_left_paren = sum(1 for c in res_dict['prolog'] if c == '(')
        num_right_paren = sum(1 for c in res_dict['prolog'] if c == ')')
        diff = num_left_paren - num_right_paren
        if diff > 0:
            res_dict['prolog'] = res_dict['prolog'] + ')' * diff
        res_dict.pop('text')
        res_dict['prolog'] = res_dict['prolog'].split(':-')[0].split('%')[0]
    return entry


def by_a_post_process(entries):
    return parallel_run(_a_post_process, entries)


def exec(entry):
    res = get_denotation(entry['prolog'])
    if res is not None:
        return "result", res
    else:
        return "exception", None


def result_eq(result1, result2):
    # print(f"{result1}, {result2}, {set(result1) == set(result2)}")
    if result1 == [] or result2 == []:
        return False
    return result1 == result2


filter_getter = {
    'gen_a': {'post_proc': by_a_post_process,
              'dedup': partial(by_dedup, field='prolog'),
              'exec': partial(by_exec, func=exec),
              'majority_vote': partial(by_majority_vote, check_equal_func=result_eq),
              'argmax': by_max_logprob},
    'gen_q': {'post_proc': partial(text_to_field, field='nl'),
              'length': partial(by_length, field='nl'),
              'dedup': partial(by_dedup, field='nl')}
}
