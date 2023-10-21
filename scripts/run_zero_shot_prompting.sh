export TOKENIZERS_PARALLELISM=false
export GEO_PATH=src/metrics/geoquery

model_type=api
model_name=code-davinci-002
temperature=0.8
field=gen_a

task_name=geoquery
filter_type=mv  # base, exec, mv

infer_file=data/${task_name}/dev.json
pred_name=pred-temp${temperature}


run_dir=outputs/${task_name}/${model_name}/zero_shot_prompting
mkdir -p ${run_dir}

pred_file=${run_dir}/${pred_name}.json
cmd="python api_inferencer.py \
    hydra.run.dir=${run_dir} \
    task_config=${task_name} \
    model_config=${model_type}-${field} \
    model_name=${model_name} \
    dataset_reader.dataset_path=${infer_file} \
    dataset_reader.n_tokens=${n_tokens} \
    model_config.generation_kwargs.temperature=${temperature} \
    index_reader=null \
    output_file=${pred_file}"
echo $cmd
eval $cmd



pred_filtered_file=${run_dir}/${pred_name}-${filter_type}.json
cmd="python filter.py \
  hydra.run.dir=${run_dir} \
  task_config=${task_name} \
  filter_config=${field}-${filter_type} \
  dataset_path=${pred_file} \
  output_file=${pred_filtered_file} \
  at_least_one=true \
  eval=true"
echo $cmd
eval $cmd
