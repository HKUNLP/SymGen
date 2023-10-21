from src.utils.misc import App
from src.dataset_readers.dataset_wrappers.base_dsw import ABC

field_getter = App()


@field_getter.add("q")
def get_q(entry):
    # in-context example for few-shot generating question
    return f"Natural Language: {entry['nl']}"


@field_getter.add("search_q")
def get_search_q(entry):
    return entry['nl']


@field_getter.add("a")
def get_a(entry):
    return entry['bash']


@field_getter.add("qa")
def get_qa(entry):
    # in-context example for few-shot generating answer
    return f"Natural Language: {entry['nl']}\nBash commands: {entry['bash']}"


@field_getter.add("gen_q")
def get_gen_q_instruction(entry):
    prompt = "Translate the natural language description to bash commands.\n\n" \
             "{ice_prompt}Natural Language: "
    return prompt


@field_getter.add("gen_a")
def get_gen_a_instruction(entry):
    prompt = "Translate the natural language description to bash commands.\n\n" \
             "{ice_prompt}Natural Language: {question}\nBash Commands: "
    prompt = prompt.format(question=entry['nl'], ice_prompt='{ice_prompt}')
    return prompt


class DatasetWrapper(ABC):
    name = "nl2bash"
    question_field = "nl"
    answer_field = "bash"
    hf_dataset = 'src/dataset/nl2bash.py'
    hf_dataset_name = 'nl2bash'
    field_getter = field_getter
