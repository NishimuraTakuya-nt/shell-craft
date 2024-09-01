#!/usr/bin/env python3

# このスクリプトは、BitwardenからFIDO2クレデンシャルを取得し、
# sts get-session-tokenコマンドを使用してAWSのセッショントークンを取得したかったが、
# 現状FIDO2クレデンシャルを使用してAWS CLIの認証を行うことはできない。
import json
import subprocess
import boto3
import os
from dotenv import load_dotenv
import base64

# .envファイルから環境変数を読み込む
load_dotenv()

BITWARDEN_ITEM_ID = os.getenv('BITWARDEN_ITEM_ID')
AWS_MFA_SERIAL = os.getenv('AWS_MFA_SERIAL')

def unlock_bitwarden():
    try:
        subprocess.run(["bw", "unlock", "--check"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        master_password = os.getenv('BW_PASSWORD')
        if not master_password:
            print("Bitwarden is locked. Please set BW_PASSWORD environment variable.")
            exit(1)
        result = subprocess.run(["bw", "unlock", master_password], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to unlock Bitwarden: {result.stderr}")
            exit(1)
        os.environ['BW_SESSION'] = result.stdout.strip()

def get_fido2_credential_from_bitwarden(item_id):
    try:
        item_data = subprocess.check_output(["bw", "get", "item", item_id]).decode()
        item_json = json.loads(item_data)
        fido2_credentials = item_json['login']['fido2Credentials']
        if fido2_credentials and len(fido2_credentials) > 0:
            return fido2_credentials[0]
        else:
            print("No FIDO2 credentials found in the Bitwarden item")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error retrieving item from Bitwarden: {e}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing Bitwarden item data: {e}")
        return None

def get_aws_session_token(fido2_credential):
    sts_client = boto3.client('sts')
    try:
        # ここでFIDO2クレデンシャルを使用してAWSの認証を行う
        # 注意: 現在のAWS SDKは直接FIDO2/WebAuthn認証をサポートしていないため、
        # カスタム実装が必要になる可能性があります fixme どうやら現状はできない
        response = sts_client.get_session_token(
            SerialNumber=AWS_MFA_SERIAL,
            TokenCode=base64.b64encode(fido2_credential['credentialId'].encode()).decode()
        )
        return response['Credentials']
    except Exception as e:
        print(f"Error getting AWS session token: {e}")
        return None

def main():
    if not all([BITWARDEN_ITEM_ID, AWS_MFA_SERIAL]):
        print("Error: One or more required environment variables are not set")
        exit(1)

    unlock_bitwarden()

    fido2_credential = get_fido2_credential_from_bitwarden(BITWARDEN_ITEM_ID)
    if not fido2_credential:
        exit(1)

    credentials = get_aws_session_token(fido2_credential)
    if not credentials:
        exit(1)

    print(json.dumps({
        "Version": 1,
        "AccessKeyId": credentials['AccessKeyId'],
        "SecretAccessKey": credentials['SecretAccessKey'],
        "SessionToken": credentials['SessionToken'],
        "Expiration": credentials['Expiration'].isoformat()
    }))

if __name__ == "__main__":
    main()
