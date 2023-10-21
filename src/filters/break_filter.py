#!/usr/bin/python3
# -*- coding: utf-8 -*-
from src.filters.filter_tool import *
import importlib
renorm = importlib.import_module('src.metrics.break.evaluator').renorm
format_qdmr = importlib.import_module('src.metrics.break.evaluator').format_qdmr
QDMRToQDMRStepTokensConverter = importlib.import_module('src.metrics.break.evaluator').QDMRToQDMRStepTokensConverter
LogicalFromStructuralMatcher = importlib.import_module('src.metrics.break.evaluator').LogicalFromStructuralMatcher


def exec(entry):
    try:
        pred = format_qdmr(renorm(entry['decomposition']))
        converter = QDMRToQDMRStepTokensConverter()
        decomp_lf = converter.convert(question_id=0, question_text=entry['question_text'],
                                      decomposition=pred.to_break_standard_string())
        # decomp_lf is not string obejct, we use original text as the result
        # return "result", (entry['decomposition'], entry['question_text'])
        return "result", pred.to_break_standard_string()
    except:
        return "exception", None


def result_eq(result1, result2):
    return result1 == result2
    # converter = QDMRToQDMRStepTokensConverter()
    # matcher = LogicalFromStructuralMatcher()
    # pred1 = format_qdmr(renorm(result1[0]))
    # pred2 = format_qdmr(renorm(result2[0]))
    #
    # decomp_lf1 = converter.convert(question_id=0, question_text=result1[1],
    #                                decomposition=pred1.to_break_standard_string())
    # decomp_lf2 = converter.convert(question_id=1, question_text=result1[1],
    #                                decomposition=pred2.to_break_standard_string())
    # return matcher.is_match(question_id=0, question_text=result1[1], graph1=decomp_lf1, graph2=decomp_lf2)


filter_getter = {
    'gen_a': {'post_proc': partial(text_to_field, field='decomposition'),
              'dedup': partial(by_dedup, field='decomposition'),
              'exec': partial(by_exec, func=exec),
              'majority_vote': partial(by_majority_vote, check_equal_func=result_eq),
              'argmax': by_max_logprob},
    'gen_q': {'post_proc': partial(text_to_field, field='question_text'),
              'length': partial(by_length, field='question_text'),
              'dedup': partial(by_dedup, field='question_text')}
}
