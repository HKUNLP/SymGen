# encoding=utf8

from .spider_exact_match import compute_exact_match_metric
from .spider_test_suite import compute_test_suite_metric


class EvaluateTool:
    def __init__(self, test_suite_db_dir=None):
        self.test_suite_db_dir = test_suite_db_dir

    def evaluate(self, preds, golds):
        # preds is list of predicted texts, while golds is list of dicts
        exact_match = compute_exact_match_metric(preds, golds)
        test_suite = compute_test_suite_metric(preds, golds, db_dir=self.test_suite_db_dir)
        return {**exact_match, **test_suite}
