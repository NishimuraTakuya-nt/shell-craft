#!/bin/bash
set -e

# 設定ファイルのパス
CONFIG_FILE=".env"

# 設定ファイルが存在する場合、読み込む
if [ -f "$CONFIG_FILE" ]; then
    while IFS='=' read -r key value
    do
        # コメントと空行をスキップ
        [[ $key =~ ^#.*$ ]] || [[ -z $key ]] && continue
        # 環境変数として設定
        export "$key"="$value"
    done < "$CONFIG_FILE"
fi

# 環境変数を使用する例
echo "API_KEY: ${IAM_MFA_ARN:-Not set}"

# ここにスクリプトの主要な処理を記述
# ...