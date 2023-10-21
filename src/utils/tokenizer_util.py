#!/usr/bin/python3
# -*- coding: utf-8 -*-
from transformers import AutoTokenizer

def get_tokenizer(model_name):
    try: 
        tok = AutoTokenizer.from_pretrained(model_name)
    except:
        # using gpt2 tokenizer for api models (mainly for control token length)
        tok = AutoTokenizer.from_pretrained("gpt2")
    return tok