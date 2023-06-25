from patchwork.transfers import rsync
from fabric import Connection
from pylambdacloud.api import get_terminate_cmd
import logging


class SSHConnection:
    """The SSHConnection class is designed to manage an SSH connection to a Lambda Cloud instance.

    The class provides functionality to initialize a connection, transfer files from
    the local system to the remote instance, construct a command list to be executed
    on the remote instance within a tmux session, and execute these commands.

    The class appends the command to terminate the instance once all the user commands have
    been executed.

    Notably, this class integrates tmux into the workflow, allowing for session management
    on the remote instance, ensuring that long-running tasks can be executed and monitored
    without the need of maintaining an active SSH connection.
    """

    def __init__(
        self, instance_info, user="ubuntu", tmux_session_name="pylambdacloud"
    ) -> None:
        """Initializes the SSHConnection class.
        Args:
            instance_info (dict): A dictionary containing the instance_id and host of the remote instance.
            user (str): The username to be used when connecting to the remote instance.
            tmux_session_name (str): The name of the tmux session to be created on the remote instance.
        """
        logging.info(f"Connecting to instance...\n{instance_info}")
        self.host = instance_info["host"]
        self.instance_id = instance_info["instance_id"]
        self.user = user
        self.c = Connection(self.host, user=self.user)
        self.tmux_session_name = tmux_session_name
        self.terminate_cmd = get_terminate_cmd(self.instance_id)
        self.executed_commands = []

    def transfer_files(self, copy_pairs):
        """Transfers files or directories from the local system to the remote instance.
        Args:
            copy_pairs (list): A list of lists or tuples, where each contains the source and destination paths.
        """
        for src, dst in copy_pairs:
            rsync(
                self.c,
                source=src,
                target=dst,
            )

    def construct_command_from_list(self, commands):
        """Constructs the command to be executed on the remote instance, which consists of:
        1. Creating a tmux session
        2. Sending the user commands to the tmux session
        3. Sending the command to terminate the instance to the tmux session.

        Args:
            commands (list): A list of commands to be executed on the remote instance.
        """
        full_cmd = f"tmux new-session -d -s {self.tmux_session_name};"
        user_cmd = ""
        for command in commands:
            user_cmd += f"{command};"
        user_cmd += self.terminate_cmd
        full_cmd += f"tmux send-keys -t {self.tmux_session_name} '{user_cmd}' Enter;"
        return full_cmd

    def _run_command_and_terminate(self, command):
        """Executes the command on the remote instance and terminates the instance.
        Args:
            command (str): The command to be executed on the remote instance.
        """
        self.c.run(command)
        self.executed_commands.append(command)
        self.c.close()

    def run_commands_and_terminate(self, command_list):
        """Executes the commands on the remote instance and terminates the instance.
        Args:
            command_list (list): A list of commands to be executed on the remote instance.
        """
        full_cmd = self.construct_command_from_list(command_list)
        self._run_command_and_terminate(full_cmd)
