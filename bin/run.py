import argparse
from pylambdacloud.ssh import SSHConnection
from pylambdacloud.launch_instance import launch_instance, is_active
from pylambdacloud.utils import parse_config
import time
import logging


def setup_logger(level):
    # Define the logging format
    logging.basicConfig(format="%(levelname)s: %(message)s", level=level)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="path to config file", required=True)
    parser.add_argument(
        "--log",
        help="logging level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    setup_logger(args.log)
    config = parse_config(args.config)
    instance_info = launch_instance(config)
    instance_id = instance_info["instance_id"]
    while not is_active(instance_id):
        logging.info("Waiting for instance to become active...")
        time.sleep(5)
    logging.info("Instance is active!")
    instance_id = instance_info["instance_id"]
    ssh_connection = SSHConnection(instance_info)
    ssh_connection.transfer_files(config["copy"])
    ssh_connection.run_commands_and_terminate(config["commands"])
    logging.info("Executed commands on instance.")
    logging.debug(f"Full command: {ssh_connection.executed_commands[0]}")
    logging.info(
        "The instance will be terminated when the user commands finish executing."
    )
    logging.info(
        f"You can monitor the instance with the following command:\n\t"
        f"ssh -t {ssh_connection.user}@{ssh_connection.host} "
        f"tmux attach-session -t '{ssh_connection.tmux_session_name}'"
    )
