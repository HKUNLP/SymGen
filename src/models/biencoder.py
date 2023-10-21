import torch
from transformers import AutoModel, PretrainedConfig, PreTrainedModel


class BiEncoderConfig(PretrainedConfig):
    model_type = "BiEncoder"

    def __init__(
            self,
            q_model_name=None,
            ctx_model_name=None,
            norm_embed=False,
            **kwargs
    ):
        super().__init__(**kwargs)
        self.q_model_name = q_model_name
        self.ctx_model_name = ctx_model_name
        self.norm_embed = norm_embed


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)


class BiEncoder(PreTrainedModel):
    config_class = BiEncoderConfig

    def __init__(self, config):
        super(BiEncoder, self).__init__(config)
        assert config.q_model_name is not None or config.ctx_model_name is not None

        if config.q_model_name is not None:
            self.question_model = AutoModel.from_pretrained(config.q_model_name)
        else:
            self.question_model = None

        if config.ctx_model_name is not None:
            self.ctx_model = AutoModel.from_pretrained(config.ctx_model_name)
        else:
            self.ctx_model = None

        if self.question_model is None and self.ctx_model is not None:
            self.question_model = self.ctx_model
        if self.question_model is not None and self.ctx_model is None:
            self.ctx_model = self.question_model

        self.norm_embed = config.norm_embed

    def encode(self, input_ids, attention_mask, encode_ctx=False, **kwargs):
        if encode_ctx:
            enc_emb = self.ctx_model(input_ids, attention_mask)
        else:
            enc_emb = self.question_model(input_ids, attention_mask)
        enc_emb = mean_pooling(enc_emb, attention_mask)
        if self.norm_embed:
            enc_emb = enc_emb / enc_emb.norm(p=2, dim=-1, keepdim=True)
        return enc_emb
