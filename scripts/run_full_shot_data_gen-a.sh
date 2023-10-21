export TOKENIZERS_PARALLELISM=false
export HYDRA_FULL_ERROR=1
export GEO_PATH=src/metrics/geoquery


model_type=api
model_name=code-davinci-002
n_tokens=7000
temperature=0.8
field=gen_a
shot=full
task_name=geoquery
filter_type=mv  # base, exec, mv
filter_entry=true  # for mv
temperature=0.8

run_dir=outputs/${task_name}/${model_name}/${shot}_shot-gen
index_file=data/${task_name}/train.json


for q_file_name in q-temp0.8-base
# for q_file_name in q-temp0.6-base q-temp0.8-base q-temp1-base
do
  infer_file=${run_dir}/${q_file_name}.json
  pred_name=${q_file_name}-a-temp${temperature}
  pred_file=${run_dir}/${pred_name}.json


  infer_file_retrieved=${run_dir}/${q_file_name}-retrieved.json
  cmd="python dense_retriever.py \
      output_file=${infer_file_retrieved} \
      num_ice=128 \
      task_name=${task_name} \
      dataset_reader.dataset_path=${infer_file} \
      index_reader.dataset_path=${index_file} \
      faiss_index=${run_dir}/index"
  echo $cmd
  eval $cmd


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
#  eval $cmd
done


#python scripts/mix_jsonl.py \
#  ${index_file} \
#  outputs/${task_name}/${model_name}/${shot}_shot-gen/q-temp0.6-base-a-temp${temperature}-${filter_type}-filter_entry.json \
#  outputs/${task_name}/${model_name}/${shot}_shot-gen/q-temp0.8-base-a-temp${temperature}-${filter_type}-filter_entry.json \
#  outputs/${task_name}/${model_name}/${shot}_shot-gen/q-temp1-base-a-temp${temperature}-${filter_type}-filter_entry.json \
#  outputs/${task_name}/${model_name}/${shot}_shot-gen/q-merge-base-a-temp${temperature}-${filter_type}-filter_entry.json