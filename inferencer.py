import glob
import json
import os
import logging
import hydra
import hydra.utils as hu
import torch
import tqdm
from omegaconf import OmegaConf
from torch.utils.data import DataLoader

from src.utils.collators import DataCollatorWithPaddingAndCuda
from src.utils.statistics import show_statistics

logger = logging.getLogger(__name__)


class Inferencer:
    def __init__(self, cfg, accelerator=None) -> None:
        self.dataset_reader = hu.instantiate(cfg.dataset_reader)
        self.gen_field = cfg.dataset_reader.field

        self.accelerator = accelerator
        self.output_file = cfg.output_file
        # OmegaConf DictConfig to dict
        self.generation_kwargs = OmegaConf.to_object(cfg.model_config.generation_kwargs)

        self.model, self.dataloader = self.init_model_dataloader(cfg)

    def init_model_dataloader(self, cfg):
        self.dataset_reader.shard(self.accelerator)

        if self.accelerator.is_main_process:
            show_statistics(self.dataset_reader.encoded_dataset, "main dataset")
            show_statistics(self.dataset_reader.index_reader.encoded_dataset, "index dataset")

        co = DataCollatorWithPaddingAndCuda(tokenizer=self.dataset_reader.tokenizer, device=self.accelerator.device)
        dataloader = DataLoader(self.dataset_reader, batch_size=cfg.batch_size, collate_fn=co)

        model = hu.instantiate(cfg.model).eval()
        model = self.accelerator.prepare(model)

        if hasattr(model, "module"):
            model = model.module

        return model, dataloader

    def forward(self):
        if self.accelerator.is_main_process:
            dataloader = tqdm.tqdm(self.dataloader)
        else:
            dataloader = self.dataloader

        avg_ice_num = 0
        res = []
        for i, entry in enumerate(dataloader):
            metadata = entry.pop("metadata")
            with torch.no_grad():
                outputs = self.model.generate(input_ids=entry.input_ids,
                                              attention_mask=entry.attention_mask,
                                              eos_token_id=self.dataset_reader.tokenizer.encode("\n")[0],
                                              pad_token_id=self.dataset_reader.tokenizer.pad_token_id,
                                              **self.generation_kwargs)
                prompt_len = int(entry.attention_mask.shape[1])
                for mdata, output in zip(metadata, outputs.tolist()):
                    mdata['generated'] = self.dataset_reader.tokenizer.decode(output[prompt_len:])
                    avg_ice_num += len(mdata['prompt_list'])
                res.extend(metadata)

        with open(f"{self.output_file}tmp_{self.accelerator.device}.bin", "w") as f:
            json.dump(res, f)

        logger.info(f"Average number of in-context examples after truncating is {avg_ice_num / len(res)}")

    def write_results(self):
        data = []
        for path in glob.glob(f"{self.output_file}tmp_*.bin"):
            with open(path) as f:
                data.extend(json.load(f))

        with open(self.output_file, "w") as f:
            json.dump(data, f)

        for path in glob.glob(f"{self.output_file}tmp_*.bin"):
            os.remove(path)
        return data


@hydra.main(config_path="configs", config_name="inferencer")
def main(cfg):
    from accelerate import Accelerator

    logger.info(cfg)
    accelerator = Accelerator()
    inferencer = Inferencer(cfg, accelerator)

    inferencer.forward()
    accelerator.wait_for_everyone()
    if accelerator.is_main_process:
        inferencer.write_results()


if __name__ == "__main__":
    main()
