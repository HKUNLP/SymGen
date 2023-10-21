from src.utils.misc import parallel_run, parallel_run_timeout
from .prolog_eval import check_denotaion_same


class EvaluateTool(object):
    def __init__(self):
        pass

    def evaluate(self, preds, golds):
        golds = [gold["prolog"] for gold in golds]
        em_results = parallel_run(eval_em_single, list(zip(preds, golds)))
        # exec_results = exec_acc(preds, golds, timeout=5)
        exec_results = parallel_run_timeout(eval_exec_single, list(zip(preds, golds)))
        print(exec_results)
        return {"em": sum(em_results) / len(golds),
                "exec": sum(e is True for e in exec_results) / len(golds)}


def eval_em_single(args):
    pred, gold = args
    return pred.strip() == gold


def eval_exec_single(args):
    pred, gold = args
    return check_denotaion_same(pred, gold)
