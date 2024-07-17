import requests
from pylambdacloud.utils import get_api_key
import json

API_KEY = get_api_key()
URL_BASE = "https://cloud.lambdalabs.com/api/v1/"


def api_get(endpoint):
    # Base API get request
    response = requests.get(URL_BASE + endpoint, auth=(API_KEY, ""))
    if response.status_code == 401:
        raise(EnvironmentError("Invalid API token. Check LAMBDA_CLOUD_API_KEY env"))
    return response


def api_post(endpoint, payload):
    # Base API post request
    response = requests.post(
        URL_BASE + endpoint,
        auth=(API_KEY, ""),
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
    )
    if response.status_code == 401:
        raise(EnvironmentError("Invalid API token. Check LAMBDA_CLOUD_API_KEY env"))
    return response


def get_offered_instances():
    """Returns a detailed list of the instance types offered by Lambda GPU Cloud.
    The details include the regions, if any, in which each instance type is currently available.
    https://cloud.lambdalabs.com/api/v1/docs#operation/instanceTypes
    """
    response = api_get("instance-types")
    return response


def launch_instance_call(payload):
    """Launches an instance with the given configuration.
    https://cloud.lambdalabs.com/api/v1/docs#operation/launchInstance
    """
    response = api_post("instance-operations/launch", payload)
    return response


def get_instance(instance_id):
    """Retrieves details of a specific instance, including whether or not the instance is running.
    https://cloud.lambdalabs.com/api/v1/docs#operation/getInstance
    """
    response = api_get(f"instances/{instance_id}")
    return response


def terminate_instance_call(payload):
    """Terminates an instance with the given configuration.
    https://cloud.lambdalabs.com/api/v1/docs#operation/terminateInstance
    """
    response = api_post("instance-operations/terminate", payload)
    return response


def get_terminate_cmd(instance_id):
    payload = {"instance_ids": [instance_id]}
    payload_json = json.dumps(payload).replace('"', '\\"')
    url = URL_BASE + "instance-operations/terminate"
    cmd = f'curl -u {API_KEY}: -H "Content-Type: application/json" -X POST -d "{payload_json}" {url}'
    return cmd
