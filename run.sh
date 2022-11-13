#!/usr/bin/env bash

log_dir=$(date +'%m-%d-%Y')
mkdir ./logs/${log_dir} > /dev/null 2>&1

python app.py >> ./logs/${log_dir}/log 2>&1
