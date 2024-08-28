#!/bin/bash

load_env_vars() {
    local config_file="${1:-.env}"

    if [ -f "$config_file" ]; then
        while IFS='=' read -r key value
        do
            # コメントと空行をスキップ
            [[ $key =~ ^#.*$ ]] || [[ -z $key ]] && continue
            # 環境変数として設定
            export "$key"="$value"
        done < "$config_file"
    else
        echo "Warning: Configuration file $config_file not found." >&2
    fi
}

# このスクリプトが直接実行された場合のみ関数を実行
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    load_env_vars "$@"
fi