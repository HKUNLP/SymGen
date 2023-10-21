# SymGen

This repo contains source code of our EMNLP'23 paper [Generating Data for Symbolic Language with Large Language Models](https://arxiv.org/abs/2305.13917). 

This is another successor of our previous works, i.e., [ZeroGen](https://arxiv.org/abs/2202.07922), [ProGen](https://arxiv.org/abs/2210.12329) and [SunGen](https://arxiv.org/abs/2205.12679) that employ LLMs as data generators. Some codes are adapted from [CEIL](https://github.com/HKUNLP/icl-ceil).

TL;DR:
- Annotating symbolic languages (e.g., SQL, Bash, Python, TOP, QDMR, etc.) manually is expensive and time-consuming.
- We use LLMs for generating data for symbolic language via an informative prompt to steer generation and an agreement-based verifier to improve data correctness.
- We show that the generated data can be used to train a much smaller task model that behaves well when compared with the data generator.


## Install
```
git clone --recurse-submodules git@github.com:HKUNLP/SymGen.git
conda env create -n symgen python=3.10
conda activate symgen
pip install -r requirements.txt
```

## Usage
**Note**: This repo initially uses Codex model which is not available currently, so you may need to require access [here](https://platform.openai.com/docs/deprecations/2023-03-20-codex-models). The implemented filtering processes are mostly based on logprob, if you want to use ChatGPT or GPT-4 as data generators, which don't provide such information, you should modify the filtering process.

The core codes are under `src`. We provide some scripts in `scripts` directory:
- `run_data_gen-q.sh` is used to generate *question* for a given task in zero-shot or few-shot way.
- `run_few_shot_data_gen-a.sh` is used to generate *answer* (i.e., symbolic language) with given a few in-context examples. 
- `run_full_shot_data_gen-a.sh` is used to generate *answer* with retrieved in-context examples given a large pool of available examples. 
- `run_zero_shot_prompting.sh`, `run_few_shot_prompting.sh` and `run_full_shot_prompting.sh` are not related to data generation, they are scripts used to directly do prompting on the evaluation set.

You can run the command to do specific tasks, e.g., 
```
bash scripts/run_data_gen-q.sh
```

Some notes:
- We provide three types of filtering method when obtaining a proper answer, i.e., `base`, `exec` (execution), `mv` (majority vote), see `config/filter_config/gen_a-*.yaml` and `src/filters/` for details. 
- We provide API model and huggingface local model as data generators, see `config/model_config/`. We use API model in the paper, and the huggingface local models are not highly tested.
- For SQL, we consider spider dataset, so each instance has an atrribute `db_path` pointing to its database position, you may need to change based on where the spider database is. We use [test_suite](https://github.com/elementai/test-suite-sql-eval) evaluation, so you should provide a test_database path in `configs/task_config/spider.yaml`.
- For Prolog, check `pyswip` is installed for Prolog execution through python.

Add `+dataset_reader.ds_size=2` to only inference 2 data points for debugging.

We keep some data processing scripts in each symbolic language directory under `scripts/*`. For example, create few-shot file for Spider dataset
```shell script
python scripts/spider/split_few_shot.py
```
This will create several files in data dir, e.g., `10_shot.json` contains 10 examples from train set as demonstrations, 
`dev_10_shot.json` is the `dev.json` with additional `ctxs` field indicating few-shot example index in `10_shot.json`. 
```text
data
└── spider
    ├── dev.json # full dev file, json lines
    ├── dev_10_shot.json  # dev file with 10-shots, for few-shot evaluation 
    ├── 10_shot.json  # few-shot file, contains 10 few-shot examples
    ├── train.json  # original training file
    └── 10_gen_q.json  # for generating question
```
I've provide the initial data used in paper in `data/` so you can ignore `scripts/*/*.py`.

## Include a new dataset
If you want to generate data for a new task, you have to implement some task files, e.g.,
- `src/dataset_readers/dataset_wrappers/spider.py`: this specify how to construct prompt for each example
- `src/filters/spider_filter.py`: this specify several filters to use after gathering generations. Make sure to at least include `post_proc` to extract field (e.g., answer, question) in the raw generated text.
- (Optional) `src/metrics/spider/evaluator.py`: show the task metric, only used in zero/few-shot prompting and set `eval=true` when running `filter.py`.

## Generated data
We provide generated data [here](https://drive.google.com/file/d/1jKjMUlq-xDX03xVys9ARRwa1sxcstro6/view?usp=sharing).


## Citation
If you find our work helpful, please cite us:
```
@article{ye2023generating,
  title={Generating Data for Symbolic Language with Large Language Models},
  author={Ye, Jiacheng and Li, Chengzu and Kong, Lingpeng and Yu, Tao},
  journal={arXiv preprint arXiv:2305.13917},
  year={2023}
}
```