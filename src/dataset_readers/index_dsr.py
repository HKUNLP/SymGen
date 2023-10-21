import logging
import pandas as pd
import os
from src.dataset_readers.base_dsr import BaseDatasetReader

logger = logging.getLogger(__name__)


def deduplicate(dataset_wrapper, encoded_dataset):
    """deduplication """
    df = pd.DataFrame(encoded_dataset)
    df['uid'] = df['input_ids'].astype(str)
    is_dup = df.duplicated(subset=['uid'], keep='first')
    keep_idx = is_dup[~is_dup].index.values

    dataset_wrapper.dataset = dataset_wrapper.dataset.select(keep_idx)
    encoded_dataset = encoded_dataset.select(keep_idx)

    encoded_dataset = encoded_dataset.map(reassign_idx, with_indices=True)
    logger.info(f"Keeping {len(keep_idx)}/{len(df)} instances after deduplicating")
    return dataset_wrapper, encoded_dataset


def reassign_idx(example, index):
    example['metadata']['id'] = index
    return example


class IndexDatasetReader(BaseDatasetReader):

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        dataset_path = kwargs['dataset_path']
        if dataset_path is None or not os.path.exists(dataset_path):
            # make sure all items in index are unique
            self.dataset_wrapper, self.encoded_dataset = deduplicate(self.dataset_wrapper, self.encoded_dataset)
            if dataset_path is not None:
                self.dataset_wrapper.save_to_disk(dataset_path)
                logger.info(f"index dataset has been saved to {dataset_path}")