#!/bin/bash

# 使用 hf 命令行工具从 Hugging Face 下载模型
# Usage: ./download_model_from_hf.sh <repo_id> <local_dir> <max_workers> [token]

set -e

if [ $# -lt 3 ]; then
    echo "Usage: $0 <repo_id> <local_dir> <max_workers> [token]"
    echo ""
    echo "Required arguments:"
    echo "  repo_id      Hugging Face 仓库 ID (e.g. username/repo-name)"
    echo "  local_dir    本地保存路径"
    echo "  max_workers  下载最大并发数 (--max-workers)"
    echo ""
    echo "Optional arguments:"
    echo "  token        Hugging Face 访问令牌 (--token)"
    exit 1
fi

REPO_ID=$1
LOCAL_DIR=$2
MAX_WORKERS=$3
TOKEN=${4:-}

if [ -n "$TOKEN" ]; then
    hf download "$REPO_ID" \
        --local-dir "$LOCAL_DIR" \
        --max-workers "$MAX_WORKERS" \
        --token "$TOKEN"
else
    hf download "$REPO_ID" \
        --local-dir "$LOCAL_DIR" \
        --max-workers "$MAX_WORKERS"
fi
