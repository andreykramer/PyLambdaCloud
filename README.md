# PyLambdaCloud

PyLambdaCloud provides a basic interface for launching tasks on [Lambda Cloud](https://cloud.lambdalabs.com/) instances using python. PyLambdaCloud implements a convenient way to launch an instance, transfer files from your local machine to the remote instance, and execute commands on the instance. After the user-defined commands are executed on the Lambda Cloud instance, the instance is programmatically terminated from within itself. This feature eliminates the need for manual intervention to terminate the instance, thereby avoiding unnecessary running time and associated costs.

PyLambdaCloud launches a `tmux` session in the remote instance, ensuring that long-running tasks can be executed and monitored without the need for maintaining an active SSH connection.

## Repository Structure

The repository is structured as follows:

- `bin/`: Contains the `run.py` script, which is the main entry point for using PyLambdaCloud.
- `configs/`: Contains examples of configuration files in JSON format.
- `pylambdacloud/`: The main package directory.
  - `api.py`: Contains functions for interacting with the Lambda Cloud API.
  - `select_instance.py`: Contains functions for selecting and sorting instances based on price and availability.
  - `launch_instance.py`: Contains functions for launching cloud instances.
  - `ssh.py`: Contains the `SSHConnection` class for managing SSH connections and executing commands on remote instances.
  - `test_select_instance.py`: Contains unit tests for `select_instance.py`.
  - `utils.py`: Contains utility functions, such as fetching the API key and parsing configuration files.
- `setup.py`: Contains the package setup script.

## Quickstart

### Setting Up Lambda Cloud

Before using PyLambdaCloud, you'll need to set up your Lambda Cloud account:

1. **Create an SSH key pair.** [Instructions](https://docs.oracle.com/en/cloud/cloud-at-customer/occ-get-started/generate-ssh-key-pair.html). This will be used to securely connect to your instances. Once you have generated the SSH key pair, add the public key to the SSH keys section in the Lambda Cloud dashboard. The name given to the SSH key in the dashboard is the one that you'll later include in the `ssh_key_names` list of the configuration file. 
2. **Get your API key.** Navigate to the API keys section of the Lambda Cloud dashboard and generate a new API key.
3. **Set the `LAMBDA_CLOUD_API_KEY` environment variable.** In your shell (or in your shell's configuration file such as `.bashrc` or `.bash_profile` for Bash, or `.zshrc` for Zsh), export your API key as follows:
    ```
    export LAMBDA_CLOUD_API_KEY=your_api_key_here
    ```

### Running PyLambdaCloud

1. **Clone the repository.**
    ```
    git clone https://github.com/andreykramer/pylambdacloud.git
    cd pylambdacloud
    ```
2. **Install the package.**
    ```
    pip install .
    ```
3. **Run a task.**
    ```
    python bin/run.py --config configs/example_config.json
    ```
   This command will launch an instance, transfer files specified in the configuration to the instance, and run commands on the instance as specified in the configuration. The example configuration copies the `setup.py`
   file to the instance, prints its content, waits for 30 seconds and terminates. Example output:
    - Local machine:
    ```
    INFO: Executed commands on instance.
    DEBUG: Full command: tmux new-session -d -s pylambdacloud;tmux send-keys -t pylambdacloud 'cat '/tmp/setup.py';sleep 30;curl -u [API_KEY]: -H "Content-Type: application/json" -X POST -d "{\"instance_ids\": [\"[INSTANCE_ID]\"]}" https://cloud.lambdalabs.com/api/v1/instance-operations/terminate' Enter;
    INFO: The instance will be terminated when the user commands finish executing.
    INFO: You can monitor the instance with the following command:
            ssh -t ubuntu@[IP] tmux attach-session -t 'pylambdacloud'
    ```
    - Remote instance (entered using the ssh command printed above):
    ```
    from setuptools import setup, find_packages

    setup(
        name="pylambdacloud",
        version="1.0",
        description="Basic tool for executing jobs in Lambda Cloud.",
        author="Andrey Kramer",
        packages=find_packages(),
        install_requires=["requests", "inquirer", "fabric", "patchwork"],
        tests_require=["pytest"],
    )
    {"data": {"terminated_instances": [{"id": "INSTANCE_ID", "ip": "[IP]", "region": {"name": "us-west-1", "description": "California, USA"}, "instance_type": {"name": "gpu_1x_a10", "price_cents_per_hour": 60, "description": "1x A10 (24 GB PCIe)", "specs": {"vcpus": 30, "memory_gib": 200, "storage_gib": 1400}}, "status": "terminated", "ssh_key_names": ["WSL"], "file_system_names": [], "hostname": "[IP].cloud.lambdalabs.com", "jupyter_token": "[TOKEN]", "jupyter_url": "[URL]"}]}}
    
    ubuntu@[IP]:~$ client_loop: send disconnect: Broken pipe
    ```

## Configuration Format

The PyLambdaCloud package uses a JSON configuration file to define the tasks to be executed. Here is an example of a configuration file:

```json
{
    "launch_options": {
        "instance_type_name": null,
        "region_name": null,
        "ssh_key_names": [
            "WSL"
        ],
        "file_system_names": [],
        "quantity": 1,
        "local_ssh_key": null
    },
    "copy": [
        [
            "./setup.py",
            "/tmp/"
        ]
    ],
    "commands": [
        "cat '/tmp/setup.py'",
        "sleep 30"
    ]
}
```

- `launch_options`: Options for launching instances.
    - `instance_type_name`: The type of instance to be launched. If null, the user will be prompted to select an instance type.
    - `region_name`: The region in which the instance should be launched. If null, the user will be prompted to select a region.
    - `ssh_key_names`: An array of names of SSH keys to be used for the instances.
    - `file_system_names`: An array of names of file systems to be used for the instances.
    - `quantity`: The number of instances to be launched. Currently only 1 is supported.
    - `local_ssh_key`: The full path to the private key that matches one of uploaded in `ssh_key_names`. If specified: only the specified private key is being used, no attempts to use every key from ~/.ssh directory.

- `copy`: An array of arrays, where each inner array represents a pair of source and destination paths for file transfer operations.

- `commands`: An array of commands to be executed on the remote instance.

## Disclaimer

Please note that this is an independent project and is not officially affiliated with Lambda Cloud. Although this project aims to facilitate the interaction with Lambda Cloud instances, it is not supported or endorsed by Lambda Cloud.

Additionally, please be aware that the current version of PyLambdaCloud lacks comprehensive error handling. As a result, unexpected scenarios or edge cases might result in unhandled exceptions or errors. Importantly, **errors could potentially lead to instances not being terminated properly**, which can incur unnecessary costs. Always be sure to manually verify that all instances have been terminated after your tasks are completed.

We encourage contributors to improve this aspect of the project. Always review and test the scripts in a controlled environment before using them in a production setting.
