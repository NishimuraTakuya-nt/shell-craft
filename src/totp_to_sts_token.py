#!/usr/bin/env python3

import base64
import hashlib
import hmac
import json
import os
import struct
import subprocess
import time
from datetime import datetime, timedelta

import boto3
import pytz
from dotenv import load_dotenv

# .env ファイルから環境変数を読み込む
load_dotenv()


# 環境変数の取得と検証を行う関数
def get_env_var(var_name):
    value = os.getenv(var_name)
    if not value:
        print(f"Error: {var_name} environment variable is not set.")
        exit(1)
    return value


# 必要な環境変数を取得
BW_PASSWORD = get_env_var('BW_PASSWORD')
BW_ITEM_ID = get_env_var('BW_ITEM_ID')
BW_MFA_SECRET_KEY_NAME = get_env_var('BW_MFA_SECRET_KEY_NAME')
IAM_MFA_ARN = get_env_var('IAM_TOTP_MFA_ARN')
PROFILE_NAME = get_env_var('PROFILE_NAME')
# キャッシュファイルのパス
CACHE_FILE = os.path.expanduser('~/.aws/aws_sts_session_cache.json')


# Bitwardenのアンロック
def unlock_bitwarden():
    try:
        # Bitwardenが既にアンロックされているかチェック
        subprocess.run(["bw", "unlock", "--check"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        # Bitwardenをアンロック
        result = subprocess.run(["bw", "unlock", BW_PASSWORD, "--raw"], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to unlock Bitwarden: {result.stderr}")
            exit(1)
        # セッションキーを環境変数に設定
        os.environ['BW_SESSION'] = result.stdout.strip()


# BitwardenからMFAシークレットを取得
def get_mfa_secret():
    # Bitwardenから項目を取得
    result = subprocess.run(["bw", "get", "item", BW_ITEM_ID], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Failed to get item from Bitwarden: {result.stderr}")
        exit(1)

    # JSONレスポンスをパース
    item_data = json.loads(result.stdout)

    # MFAシークレットを検索
    for field in item_data['fields']:
        if field['name'] == BW_MFA_SECRET_KEY_NAME:
            return field['value']

    print(f"MFA secret with name {BW_MFA_SECRET_KEY_NAME} not found in the item.")
    exit(1)


# TOTPコードを生成
def generate_totp(secret):
    def hotp(secret, intervals_no):
        key = base64.b32decode(secret, True)
        msg = intervals_no.to_bytes(8, 'big')
        h = hmac.new(key, msg, hashlib.sha1).digest()
        offset = h[-1] & 0xf
        return struct.unpack('>I', h[offset:offset + 4])[0] & 0x7fffffff

    intervals_no = int(time.time()) // 30
    return '{:06d}'.format(hotp(secret, intervals_no) % 1000000)


# AWSセッショントークンを取得
def get_aws_session_token(totp_code):
    try:
        session = boto3.Session(profile_name=PROFILE_NAME)
        sts_client = session.client('sts')
        response = sts_client.get_session_token(
            DurationSeconds=129600,
            SerialNumber=IAM_MFA_ARN,
            TokenCode=totp_code
        )
        credentials = response['Credentials']
        credentials['Expiration'] = credentials['Expiration'].isoformat()
        save_credentials_to_cache(credentials)
        return credentials
    except Exception as e:
        print(f"Failed to get AWS session token: {str(e)}")
        exit(1)


# キャッシュからクレデンシャルを読み込む
def load_cached_credentials():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
        expiration = datetime.fromisoformat(cache['Expiration'])
        now = datetime.now(pytz.UTC)
        if expiration.replace(tzinfo=pytz.UTC) > now + timedelta(minutes=5):
            return cache
    return None


# クレデンシャルをキャッシュに保存
def save_credentials_to_cache(credentials):
    with open(CACHE_FILE, 'w') as f:
        json.dump(credentials, f)


def main():
    cached_credentials = load_cached_credentials()
    if cached_credentials:
        print(json.dumps({
            'Version': 1,
            'AccessKeyId': cached_credentials['AccessKeyId'],
            'SecretAccessKey': cached_credentials['SecretAccessKey'],
            'SessionToken': cached_credentials['SessionToken'],
            'Expiration': cached_credentials['Expiration']
        }))
        return

    unlock_bitwarden()
    mfa_secret = get_mfa_secret()
    totp_code = generate_totp(mfa_secret)
    credentials = get_aws_session_token(totp_code)

    print(json.dumps({
        'Version': 1,
        'AccessKeyId': credentials['AccessKeyId'],
        'SecretAccessKey': credentials['SecretAccessKey'],
        'SessionToken': credentials['SessionToken'],
        'Expiration': credentials['Expiration']
    }))


if __name__ == "__main__":
    main()
