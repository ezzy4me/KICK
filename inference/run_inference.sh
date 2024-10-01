PROMPT_FILE_PATH="Prompt/prompt.txt"
DATA_FILE_PATH="data/dataset_processed.json"
DATA_SAVE_PATH="results"

DATA_TYPE="default"
# DATA_TYPE="caster_only"
# DATA_TYPE="commentator_only"

MODEL="gpt-4o"
# MODEL="gemma-9b-it"
# MODEL="llama"

FORMATTED_TIME=$(date +"%y_%m_%d_%H_%M_%S")

python inference.py \
--prompt_file_path ${PROMPT_FILE_PATH} \
--data_file_path ${DATA_FILE_PATH} \
--save_path ${DATA_SAVE_PATH}/${MODEL}_${DATA_TYPE}_${FORMATTED_TIME}.json \
--model ${MODEL} \
--data_type ${DATA_TYPE} \
>>logs/${MODEL}_${FORMATTED_TIME}_${DATA_TYPE}.log \
