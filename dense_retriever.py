import json
import logging
import faiss
import hydra
import hydra.utils as hu
import numpy as np
import torch
import tqdm
from transformers import set_seed
from torch.utils.data import DataLoader
from src.utils.misc import save_jsonl
from src.utils.collators import DataCollatorWithPaddingAndCuda
from src.models.biencoder import BiEncoder

logger = logging.getLogger(__name__)


class DenseRetriever:
    def __init__(self, cfg) -> None:
        self.cuda_device = "cuda:0" if torch.cuda.is_available() else "cpu"
        self.dataset_reader = hu.instantiate(cfg.dataset_reader)
        co = DataCollatorWithPaddingAndCuda(tokenizer=self.dataset_reader.tokenizer, device=self.cuda_device)
        self.dataloader = DataLoader(self.dataset_reader, batch_size=cfg.batch_size, collate_fn=co)

        model_config = hu.instantiate(cfg.model_config)
        self.model = BiEncoder(model_config)
        self.model = self.model.to(self.cuda_device)
        self.model.eval()

        self.output_file = cfg.output_file
        self.num_ice = cfg.num_ice
        self.is_train = cfg.dataset_reader.dataset_split == "train"

        # if os.path.exists(cfg.faiss_index):
        #     self.index = faiss.read_index(cfg.faiss_index)
        # else:
        self.index = self.create_index(cfg)

    def create_index(self, cfg):
        logger.info("building index...")
        index_reader = hu.instantiate(cfg.index_reader)
        co = DataCollatorWithPaddingAndCuda(tokenizer=index_reader.tokenizer, device=self.cuda_device)
        dataloader = DataLoader(index_reader, batch_size=cfg.batch_size, collate_fn=co)

        index = faiss.IndexIDMap(faiss.IndexFlatIP(768))
        res_list = self.forward(dataloader, encode_ctx=True)
        id_list = np.array([res['metadata']['id'] for res in res_list])
        embed_list = np.stack([res['embed'] for res in res_list])
        index.add_with_ids(embed_list, id_list)

        faiss.write_index(index, cfg.faiss_index)
        logger.info(f"end building index, size {len(index_reader)}")
        return index

    def forward(self, dataloader, **kwargs):
        res_list = []
        for i, entry in enumerate(tqdm.tqdm(dataloader)):
            with torch.no_grad():
                metadata = entry.pop("metadata")
                res = self.model.encode(**entry, **kwargs)
            res = res.cpu().detach().numpy()
            res_list.extend([{"embed": r, "metadata": m} for r, m in zip(res, metadata)])
        return res_list

    def knn(self, entry, num_ice=1):
        embed = np.expand_dims(entry['embed'], axis=0)
        near_ids = self.index.search(embed, num_ice+1)[1][0].tolist()
        near_ids = near_ids[1:] if self.is_train else near_ids
        return near_ids[:num_ice]

    def find(self):
        res_list = self.forward(self.dataloader)
        data_list = []
        for entry in tqdm.tqdm(res_list):
            data = self.dataset_reader.dataset_wrapper[entry['metadata']['id']]
            ctxs = self.knn(entry, num_ice=self.num_ice)
            data['ctxs'] = ctxs
            data_list.append(data)

        save_jsonl(self.output_file, data_list)


@hydra.main(config_path="configs", config_name="dense_retriever")
def main(cfg):
    logger.info(cfg)
    set_seed(43)
    dense_retriever = DenseRetriever(cfg)
    dense_retriever.find()


if __name__ == "__main__":
    main()
