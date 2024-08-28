#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 環境変数読み込み
LOAD_ENV_SCRIPT="${SCRIPT_DIR}/load_env.sh"
if [ -f "$LOAD_ENV_SCRIPT" ]; then
    source "$LOAD_ENV_SCRIPT"
    load_env_vars
else
    echo "Error: Cannot find load_env.sh script" >&2
    exit 1
fi

# ここから実際のコマンドの処理
echo "Using API_KEY: ${IAM_MFA_ARN:-Not set}"

# その他のコマンド固有の処理
# ...