import logging
import hydra
from omegaconf import OmegaConf
from src.dataset_readers.dataset_wrappers import get_dataset_wrapper
from src.filters import get_filter
from src.metrics import get_metric
from src.utils.misc import save_jsonl, flatten_entries


logger = logging.getLogger(__name__)


class Filter:

    def __init__(self, cfg):
        task_name = cfg.task_config.task_name
        self.dataset = get_dataset_wrapper(task_name, dataset_path=cfg.dataset_path)
        self.eval = cfg.eval
        self.output_file = cfg.output_file

        metric_kwargs = OmegaConf.to_object(cfg.task_config.metrics) if cfg.task_config.metrics is not None else {}
        self.evaluator = get_metric(task_name, **metric_kwargs)
        self.task_filter = get_filter(task_name, **OmegaConf.to_object(cfg.filter_config))

    def run(self):
        entries = self.task_filter.run(list(self.dataset))
        # convert each candidates to a individual entry, used while generating q field
        entries = flatten_entries(entries)
        if self.eval:
            # flatten will overwrite predictions to entry,
            assert len(entries) == len(list(self.dataset))
            preds = [i[self.dataset.answer_field] for i in entries]
            metric = self.evaluator.evaluate(preds, list(self.dataset))
            logger.info(f"Metric: {str(metric)}")

        save_jsonl(self.output_file, entries)


@hydra.main(config_path="configs", config_name="filter")
def main(cfg):
    logger.info(cfg)
    filter = Filter(cfg)
    filter.run()


if __name__ == "__main__":
    main()
