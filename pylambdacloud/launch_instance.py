import os
from pathlib import Path
import time
import logging

from pylambdacloud.api import (
    launch_instance_call,
    get_instance,
    terminate_instance_call,
)
from pylambdacloud.select_instance import list_instance_types, prompt_for_instance_type


def check_instance_and_region_available(instance_type, region):
    if instance_type is None or region is None:
        return False
    available_instances = list_instance_types()
    if instance_type in available_instances.keys():
        if (
            region
            in available_instances[instance_type]["regions_with_capacity_available"]
        ):
            return True
        else:
            return False
    else:
        return False


def construct_payload(config):
    instance_type = config.get("instance_type_name")
    region = config.get("region_name")
    available = check_instance_and_region_available(instance_type, region)
    if available:
        return config
    else:
        print(
            "Instance type and region not available, please select another from the list:"
        )
        instance_type, region = prompt_for_instance_type()
        config["instance_type_name"] = instance_type
        config["region_name"] = region
    return config


def get_instance_info(launch_instance_response):
    instance_id = launch_instance_response.json()["data"]["instance_ids"][0]
    start_time = time.time()
    logging.info("Waiting for instance to become active...")
    while True:
        response = get_instance(instance_id)
        status = response.json()["data"]["status"]
        if is_active(instance_id):
            logging.info("Instance is active")
            break
        else:
            logging.info(f"[%d sec] Instance status: {status}", int(time.time()-start_time))
        time.sleep(5)  # wait for 5 seconds before making another request
    host = response.json()["data"]["ip"]
    instance_info = {
        "instance_id": instance_id,
        "host": host,
    }
    return instance_info


def launch_instance(config):
    launch_options_config = config["launch_options"]
    payload = construct_payload(launch_options_config)
    response = launch_instance_call(payload)
    instance_info = get_instance_info(response)
    instance_info["local_ssh_key"] = launch_options_config.get("local_ssh_key")
    return instance_info


def is_active(instance_id):
    response = get_instance(instance_id)
    return response.json()["data"]["status"] == "active"


def terminate_instance(instance_id):
    payload = {"instance_ids": [instance_id]}
    response = terminate_instance_call(payload)
    return response


if __name__ == "__main__":
    curr_file_path = Path(__file__).parent.absolute()
    example_config_path = os.path.join(
        curr_file_path.parent, "configs/example_config.json"
    )
    from pylambdacloud.utils import parse_config

    config = parse_config(example_config_path)
    print(construct_payload(config))
