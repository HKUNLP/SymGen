export TOKENIZERS_PARALLELISM=false
export HYDRA_FULL_ERROR=1


model_type=api
model_name=code-davinci-002
# model_name=text-davinci-003
field=gen_q
shots=10
task_name=nl2bash
filter_type=base  # base, exec, mv, how to verify the output

infer_file=data/${task_name}/${shots}_gen_q.json 
index_file=data/${task_name}/${shots}_shot.json  # few-shot file

run_dir=outputs/${task_name}/${model_name}/${shots}_shot-gen
mkdir -p ${run_dir}

for temperature in 0.8
do
  pred_name=q-temp${temperature}

  pred_file=${run_dir}/${pred_name}.json
  cmd="python3 api_inferencer.py \
      hydra.run.dir=${run_dir} \
      task_config=${task_name} \
      model_config=${model_type}-${field} \
      model_name=${model_name} \
      dataset_reader.dataset_path=${infer_file} \
      index_reader.dataset_path=${index_file} \
      model_config.generation_kwargs.temperature=${temperature} \
      output_file=${pred_file} \
      +dataset_reader.ds_size=2"
  echo $cmd
  eval $cmd


  pred_filtered_file=${run_dir}/${pred_name}-${filter_type}.json
  cmd="python filter.py \
      hydra.run.dir=${run_dir} \
      task_config=${task_name} \
      filter_config=${field}-${filter_type} \
      dataset_path=${pred_file} \
      output_file=${pred_filtered_file} \
      eval=false"
  echo $cmd
  eval $cmd

done