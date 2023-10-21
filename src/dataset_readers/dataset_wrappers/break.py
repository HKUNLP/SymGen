from src.utils.misc import App
from src.dataset_readers.dataset_wrappers.base_dsw import *
import regex as re


field_getter = App()


def remove_double_space(string):
    return re.sub("[ ]{2,}", " ", string)


def reformat(text):
    return " ".join([f"{i + 1}#) {x.strip()}" for i, x in enumerate(text.split(";"))])


@field_getter.add("q")
def get_q(entry):
    return f"Question: {remove_double_space(entry['question_text'])}"


@field_getter.add("search_q")
def get_search_q(entry):
    return entry['question_text']


@field_getter.add("qa")
def get_qa(entry):
    return f"Question: {remove_double_space(entry['question_text'])}\n" \
           f"Answer Steps: {remove_double_space(reformat(entry['decomposition']))}"


@field_getter.add("a")
def get_a(entry):
    return remove_double_space(reformat(entry['decomposition']))


@field_getter.add("gen_q")
def get_gen_q_instruction(entry):
    prompt = "Break down a question into the requisite steps for computing its answer.\n\n" \
             "{ice_prompt}Question: "
    return prompt.format(ice_prompt="{ice_prompt}")


@field_getter.add("gen_a")
def get_gen_a_instruction(entry):
    prompt = "Break down a question into the requisite steps for computing its answer.\n\n" \
             "{ice_prompt}Question: {question}\nAnswer Steps: 1#)"
    prompt = prompt.format(question=entry['question_text'], ice_prompt='{ice_prompt}')
    return prompt


class DatasetWrapper(ABC):
    name = "break"
    question_field = "question_text"
    answer_field = "decomposition"
    hf_dataset = "break_data"
    hf_dataset_name = "QDMR"
    field_getter = field_getter
