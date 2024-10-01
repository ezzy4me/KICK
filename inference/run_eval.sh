DATA_FILE_PATH="result/processed_human_pred"


python eval.py \
--data_file_path ${DATA_FILE_PATH}.json \
>>${DATA_FILE_PATH}_eval.log\
