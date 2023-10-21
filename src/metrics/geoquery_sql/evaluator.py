# encoding=utf8
import sqlparse
from src.utils.misc import parallel_run
from third_party.spider.preprocess.get_tables import dump_db_json_schema
from .exec import compute_exec_metric
from .exact_match import compute_exact_match_metric


class EvaluateTool:
    def __init__(self):
        schema = dump_db_json_schema(
            "data/geoquery_sql/geography_db/geography_db.sqlite", "geography_db"
        )
        self.schema = {
            "db_table_names": schema["table_names_original"],
            "db_column_names": {"table_id": [i[0] for i in schema["column_names_original"]],
                                "column_name": [i[1] for i in schema["column_names_original"]]
                                },
            "db_column_types": schema["column_types"],
            "db_primary_keys": {"column_id": schema["primary_keys"]},
            "db_foreign_keys": {"column_id": [i[0] for i in schema["foreign_keys"]],
                                "other_column_id": [i[1] for i in schema["foreign_keys"]]},
        }

    def evaluate(self, preds, golds):
        # preds is list of predicted texts, while golds is list of dicts
        for g in golds:
            g.update(self.schema)
            g['query'] = g['query'].strip(';').replace("=", " = ")
        for i in range(len(preds)):
            preds[i] = preds[i].strip(';').replace("=", " = ")

        hard_em_results = parallel_run(eval_em_single, list(zip(preds, golds)))
        exec_acc = compute_exec_metric(preds, golds)
        exact_match = compute_exact_match_metric(preds, golds)
        return {"em": sum(hard_em_results) / len(golds),
                **exec_acc,
                **exact_match}


def eval_em_single(args):
    pred, gold = args
    print(pred, gold['query'])
    return pred.strip().lower() == gold['query'].strip().lower()
