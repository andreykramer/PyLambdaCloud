import pprint
import inquirer
from pylambdacloud.api import get_offered_instances


def sort_by_price_fn(item):
    return int(item[1]["price_cents_per_hour"])


def sort_instances(instances):
    sorted_instances = sorted(instances, key=sort_by_price_fn, reverse=True)
    return dict(sorted_instances)


def remove_non_available_instances(all_instances):
    # Remove instances that are not available in any region
    available_instances = {}
    for instance_type, instance_data in all_instances.items():
        if len(instance_data["regions_with_capacity_available"]) > 0:
            available_instances.update({instance_type: instance_data})
    return available_instances


def flatten_instance_information(lambdacloud_instance_information):
    """Simplifies the instance information returned by the API.
    Example:
    ```
    'gpu_1x_a10': {'instance_type': {'name': 'gpu_1x_a10',
                                  'price_cents_per_hour': 60,
                                  'description': '1x A10 (24 GB PCIe)',
                                  'specs': {'vcpus': 30,
                                            'memory_gib': 200,
                                            'storage_gib': 1400}},
                'regions_with_capacity_available': [{'name': 'us-west-1',
                                                     'description': 'California, '
                                                                    'USA'}]}}
    becomes:
    'gpu_1x_a10': {'price_cents_per_hour': 60,
                   'description': '1x A10 (24 GB PCIe)',
                   'specs': {'vcpus': 30,
                             'memory_gib': 200,
                             'storage_gib': 1400},
                   'regions_with_capacity_available': ['us-west-1']}
    """
    flattened_info = {}
    for value in lambdacloud_instance_information.values():
        flattened_info[value["instance_type"]["name"]] = {
            "price_cents_per_hour": value["instance_type"]["price_cents_per_hour"],
            "description": value["instance_type"]["description"],
            "specs": value["instance_type"]["specs"],
            "regions_with_capacity_available": [
                region["name"] for region in value["regions_with_capacity_available"]
            ],
        }
    return flattened_info


def list_instance_types():
    offered_instances = get_offered_instances()
    offered_instances = offered_instances.json()["data"]
    available_instances = remove_non_available_instances(offered_instances)
    available_instances = flatten_instance_information(available_instances)
    available_instances_sorted = sorted(
        available_instances.items(), key=sort_by_price_fn, reverse=True
    )
    available_instances_sorted = dict(available_instances_sorted)
    return available_instances_sorted


def prompt_for_instance_type():
    available_instances = list_instance_types()
    pprint.pprint(available_instances, sort_dicts=False)
    selected_instance_type = inquirer.list_input(
        message="Select an instance type", choices=list(available_instances.keys())
    )
    selected_region = inquirer.list_input(
        message="Select a region",
        choices=available_instances[selected_instance_type][
            "regions_with_capacity_available"
        ],
    )
    return selected_instance_type, selected_region


if __name__ == "__main__":
    instance_type, region = prompt_for_instance_type()
    print(f"You selected {instance_type}, {region}")
