from src.utils.misc import App
from src.dataset_readers.dataset_wrappers.base_dsw import ABC
from src.utils.spider.prompt import get_db_prompt

field_getter = App()


@field_getter.add("q")
def get_q(entry):
    return f"-- Question: {entry['question']}"


@field_getter.add("search_q")
def get_search_q(entry):
    return entry['question']


@field_getter.add("a")
def get_a(entry):
    return entry['query']


@field_getter.add("qa")
def get_qa(entry):
    return f"-- Question: {entry['question']}\n{entry['query']}"


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
    prompt = f"{db_prompt}\n" \
             "-- Write a question that can be answered based on the above tables.\n" \
             "{ice_prompt}"\
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
    # prompt = f"{db_prompt}\n" \
    prompt = f"-- Using valid SQLite, answer the following questions for the tables provided above.\n" \
             "{ice_prompt}" \
             f"-- Question: {entry['question']}\nSELECT"
    return prompt


class DatasetWrapper(ABC):
    name = "geoquery"
    question_field = "question"
    answer_field = "query"
    hf_dataset = ""
    hf_dataset_name = ""
    field_getter = field_getter
