export TOKENIZERS_PARALLELISM=false
export HYDRA_FULL_ERROR=1
export GEO_PATH=src/metrics/geoquery

model_type=api
model_name=code-davinci-002
n_tokens=7000
temperature=0.8
field=gen_a
task_name=spider
filter_type=base  # base, exec, mv

for task_name in spider
do
  infer_file=data/${task_name}/dev.json
  index_file=data/${task_name}/train.json
  pred_name=pred-temp${temperature}

  run_dir=outputs/${task_name}/${model_name}/full_shot_prompting
  mkdir -p ${run_dir}

  infer_file_retrieved=data/${task_name}/dev_full_shot.json
  cmd="python dense_retriever.py \
      output_file=${infer_file_retrieved} \
      num_ice=128 \
      task_name=${task_name} \
      dataset_reader.dataset_path=${infer_file} \
      index_reader.dataset_path=${index_file} \
      faiss_index=${run_dir}/index"
  echo $cmd
  eval $cmd

  pred_file=${run_dir}/${pred_name}.json
  cmd="python api_inferencer.py \
      hydra.run.dir=${run_dir} \
      task_config=${task_name} \
      model_config=${model_type}-${field} \
      model_name=${model_name} \
      dataset_reader.dataset_path=${infer_file_retrieved} \
      dataset_reader.n_tokens=${n_tokens} \
      index_reader.dataset_path=${index_file} \
      model_config.generation_kwargs.temperature=${temperature} \
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
done
