export TOKENIZERS_PARALLELISM=false
export HYDRA_FULL_ERROR=1
export GEO_PATH=src/metrics/geoquery

model_type=api
model_name=code-davinci-002
n_tokens=7000
temperature=0.8
field=gen_a
shot=10
task_name=spider
filter_type=mv  # base, exec, mv
filter_entry=true  # for mv
temperature=0.8

run_dir=outputs/${task_name}/${model_name}/${shot}_shot-gen
index_file=data/${task_name}/${shot}_shot.json

q_file_name=q-temp0.8-base

# for q_file_name in q-temp0.6-base q-temp1-base
for q_file_name in q-temp0.8-base
do
  infer_file=${run_dir}/${q_file_name}.json
  pred_name=${q_file_name}-a-temp${temperature}
  pred_file=${run_dir}/${pred_name}.json

  cmd="python api_inferencer.py \
      hydra.run.dir=${run_dir} \
      task_config=${task_name} \
      model_config=${model_type}-${field} \
      model_name=${model_name} \
      dataset_reader.dataset_path=${infer_file} \
      dataset_reader.n_tokens=${n_tokens} \
      index_reader.dataset_path=${index_file} \
      model_config.generation_kwargs.temperature=${temperature} \
      output_file=${pred_file}"
  echo $cmd
  eval $cmd


  pred_filtered_file=${run_dir}/${pred_name}-${filter_type}.json
  if [ "${filter_entry}" = "true" ] && [ "${filter_type}" = "mv" ]; then
    pred_filtered_file=${run_dir}/${pred_name}-${filter_type}-filter_entry.json
  fi
  cmd="python filter.py \
      hydra.run.dir=${run_dir} \
      task_config=${task_name} \
      filter_config=${field}-${filter_type} \
      dataset_path=${pred_file} \
      output_file=${pred_filtered_file} \
      filter_entry=${filter_entry} \
      eval=false"

  echo $cmd
  eval $cmd
done


python scripts/mix_jsonl.py \
  ${index_file} \
  ${run_dir}/q-temp0.6-base-a-temp${temperature}-${filter_type}-filter_entry.json \
  ${run_dir}/q-temp0.8-base-a-temp${temperature}-${filter_type}-filter_entry.json \
  ${run_dir}/q-temp1-base-a-temp${temperature}-${filter_type}-filter_entry.json \
  ${run_dir}/q-merge-base-a-temp${temperature}-${filter_type}-filter_entry.json