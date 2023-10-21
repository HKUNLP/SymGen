from src.utils.misc import parallel_run
from src.utils.mtop.top_utils import deserialize_top, get_frame_top


class EvaluateTool(object):
    def __init__(self):
        pass

    def evaluate(self, preds, golds):
        golds = [gold["logical_form"] for gold in golds]
        em_results = parallel_run(em_single, list(zip(preds, golds)))
        template_results = parallel_run(template_single, list(zip(preds, golds)))
        metrics = {"exact_match": sum(em_results) / len(golds),
                   "template_accuracy": sum(template_results) / len(golds)}
        return metrics


def em_single(args):
    pred, gold = args
    if pred.strip() == gold:
        return True
    pred_lf = deserialize_top(pred)
    gold_lf = deserialize_top(gold)
    if pred_lf is not None:
        return pred_lf.serialize() == gold_lf.serialize()
    return False


def template_single(args):
    pred, gold = args
    if pred.strip() == gold:
        return True
    pred_lf = deserialize_top(pred)
    gold_lf = deserialize_top(gold)
    if pred_lf is not None:
        target_frame = get_frame_top(pred_lf)
        predicted_frame = get_frame_top(gold_lf)
        return predicted_frame == target_frame
    return False
