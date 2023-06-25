import json
import os


def get_api_key():
    return os.getenv("LAMBDA_CLOUD_API_KEY")


def parse_config(config_path):
    with open(config_path) as f:
        config = json.load(f)
    return config
