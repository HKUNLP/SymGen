#!/usr/bin/python3
# -*- coding: utf-8 -*-
import bashlex
from nltk.translate.bleu_score import sentence_bleu
from src.filters.filter_tool import *


def exec_bash(entry):
    try:
        bashlex.parse(entry['bash'])
        return "result", list(bashlex.split(entry['bash']))
        # return "result", entry['bash']
    except:
        return "exception", None


def result_eq(result1, result2):
    # return (sentence_bleu([list(result1)], list(result2)) +
    #         sentence_bleu([list(result2)], list(result1))) / 2
    return (sentence_bleu([result1], result2) +
            sentence_bleu([result2], result1)) / 2


filter_getter = {
    'gen_a': {'post_proc': partial(text_to_field, field='bash'),
              'dedup': partial(by_dedup, field='bash'),
              'exec': partial(by_exec, func=exec_bash),
              'majority_vote': partial(by_majority_vote, check_equal_func=result_eq),
              'argmax': by_max_logprob},
    'gen_q': {'post_proc': partial(text_to_field, field='nl'),
              'length': partial(by_length, field='nl'),
              'dedup': partial(by_dedup, field='nl')}
}
