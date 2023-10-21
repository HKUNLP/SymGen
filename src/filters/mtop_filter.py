#!/usr/bin/python3
# -*- coding: utf-8 -*-
from src.utils.mtop.top_utils import deserialize_top
from src.filters.filter_tool import *


def exec(entry):
    res = deserialize_top(entry['logical_form'])
    if res is None:
        return "exception", None
    else:
        return "result", res.serialize()


def result_eq(result1, result2):
    return result1 == result2


filter_getter = {
    'gen_a': {'post_proc': partial(text_to_field, field='logical_form'),
              'dedup': partial(by_dedup, field='logical_form'),
              'exec': partial(by_exec, func=exec),
              'majority_vote': partial(by_majority_vote, check_equal_func=result_eq),
              'argmax': by_max_logprob},
    'gen_q': {'post_proc': partial(text_to_field, field='question'),
              'length': partial(by_length, field='question'),
              'dedup': partial(by_dedup, field='question')}
}
