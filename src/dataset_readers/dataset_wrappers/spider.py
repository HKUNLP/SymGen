from src.utils.misc import App
from src.dataset_readers.dataset_wrappers.base_dsw import ABC
from src.utils.spider.prompt import get_db_prompt

field_getter = App()


@field_getter.add("q")
def get_q(entry):
    db_prompt = get_db_prompt(
        db_name=entry['db_id'],
        db_root=entry['db_path'],
        schema=True,
        rows=3,
        db_content_random=True,
        reindent_aligned=True,
        question=entry['question']
    )
    return f"{db_prompt}\n-- Write a question that can be answered based on the above tables.\n" \
           f"-- Question: {entry['question']}"


@field_getter.add("search_q")
def get_search_q(entry):
    return entry['question']


@field_getter.add("a")
def get_a(entry):
    return entry['query']


@field_getter.add("qa")
def get_qa(entry):
    # in-context example for few-shot generating answer
    db_prompt = get_db_prompt(
        db_name=entry['db_id'],
        db_root=entry['db_path'],
        schema=True,
        rows=3,
        db_content_random=True,
        reindent_aligned=True,
        question=entry['question']
    )
    return f"{db_prompt}\n{entry['question']}\n{entry['query']}"


@field_getter.add("gen_q")
def get_gen_q_instruction(entry):
    db_prompt = get_db_prompt(
        db_name=entry['db_id'],
        db_root=entry['db_path'],
        schema=True,
        rows=3,
        db_content_random=True,
        reindent_aligned=True,
    )
    prompt = "{ice_prompt}"\
             f"{db_prompt}\n-- Write a question that can be answered based on the above tables.\n" \
             "-- Question: "
    return prompt


@field_getter.add("gen_a")
def get_gen_a_instruction(entry):
    db_prompt = get_db_prompt(
        db_name=entry['db_id'],
        db_root=entry['db_path'],
        schema=True,
        rows=3,
        db_content_matching=True,
        reindent_aligned=True,
        question=entry['question']
    )
    prompt = "{ice_prompt}" \
             f"{db_prompt}\n{entry['question']}\nSELECT"
    return prompt


class DatasetWrapper(ABC):
    name = "spider"
    question_field = "question"
    answer_field = "query"
    hf_dataset = "src/dataset/spider.py"
    hf_dataset_name = "spider"
    field_getter = field_getter
    ice_separator = "\n\n ** EXAMPLE SEPARATOR **\n\n"
