#!/usr/bin/env python3

from dotenv import load_dotenv
import os

def main():
    print("Hello, World!")

    # .envファイルをロード
    load_dotenv()

    # 環境変数を取得
    dev_bastion = os.getenv('DEV_BASTION')
    print(f"DEV_BASTION: {dev_bastion}")

if __name__ == "__main__":
    main()
