import logging
import hydra
import hydra.utils as hu
from inferencer import Inferencer
from src.models.api_client import run_api
from src.utils.misc import parallel_run, save_jsonl


logger = logging.getLogger(__name__)


class APInferencer(Inferencer):

    def init_model_dataloader(self, cfg):
        model = hu.instantiate(cfg.model_config.model)
        dataloader = self.dataset_reader
        return model, dataloader

    def forward(self):
        prompts = [entry['metadata']['prompt'] for entry in self.dataloader]
        logger.info(str(prompts[0]))
        logger.info(len(self.dataloader[0]['metadata']['ice_prompts_list']))
        logger.info(f"Num of ice: {len(self.dataloader[0]['metadata']['ice_prompts_list'])}")

        responses = parallel_run(run_api, args_list=prompts,
                                 n_processes=self.model.n_processes,
                                 client=self.model,
                                 **self.generation_kwargs)

        data = []
        for i, (entry, response) in enumerate(zip(self.dataloader, responses)):
            if i == 0:
                logger.info(prompts[i])
                logger.info('\n***\n'.join([str(i) for i in response][:3]))

            entry['metadata']['candidates'] = response
            entry['metadata'].pop('ice_prompts_list')
            data.append(entry['metadata'])

        save_jsonl(self.output_file, data)


@hydra.main(config_path="configs", config_name="inferencer")
def main(cfg):
    logger.info(cfg)
    inferencer = APInferencer(cfg)
    inferencer.forward()


if __name__ == "__main__":
    main()
