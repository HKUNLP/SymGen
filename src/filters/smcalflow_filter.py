#!/usr/bin/python3
# -*- coding: utf-8 -*-
from src.filters.filter_tool import *
from dataflow.core.lispress import _round_trip


def exec(entry):
    try:
        return "result", _round_trip(entry['lispress'])
    except Exception:  # pylint: disable=W0703
        return "exception", None


def result_eq(result1, result2):
    return result1 == result2


filter_getter = {
    'gen_a': {'post_proc': partial(text_to_field, field='lispress'),
              'dedup': partial(by_dedup, field='lispress'),
              'exec': partial(by_exec, func=exec),
              'majority_vote': partial(by_majority_vote, check_equal_func=result_eq),
              'argmax': by_max_logprob},
    'gen_q': {'post_proc': partial(text_to_field, field='user_utterance'),
              'length': partial(by_length, field='user_utterance'),
              'dedup': partial(by_dedup, field='user_utterance')}
}
