import paramiko
import json
import sys
import time
import logging
import argparse
import re
import csv

# Configure the logging module
logging.basicConfig(filename="ssh.log", level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Define a variable for the sleep interval
sleep_interval = 0.7

# Create an argument parser object
parser = argparse.ArgumentParser(description="A script to connect to a remote host and run some commands")

# Add arguments to the parser
parser.add_argument("-f", "--file", type=str, default="credentials.json", help="The name of the JSON file that contains the credentials")
parser.add_argument("-d", "--device", type=str, default='172.16.0.1', help="The hostname or IP address of the host. default value is 172.16.0.1")
parser.add_argument("-c", "--command", type=str, nargs="+", default=["show interface ip brief"], help="The commands to run on the host")

# Parse the arguments
args = parser.parse_args()

# Load SSH credentials from a JSON file
def load_credentials(file_name="credentials.json"):
    """Load SSH credentials from a JSON file.

    Args:
        file_name (str): The name of the JSON file that contains the credentials.

    Returns:
        dict: A dictionary that contains the username, password, and enable password.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    try:
        with open(file_name, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"The file {file_name} does not exist.")
        sys.exit(1)

# Define a function to send and receive data from the shell
def send_and_receive(shell, command, sleep_interval_inner):
    """Send a command to the shell and receive the response.

    Args:
        shell (paramiko.Channel): The SSH channel.
        command (str): The command to send.
        sleep_interval_inner (float): The interval to wait before receiving data.

    Returns:
        str: The output from the command.

    """
    try:
        # Send the command to the shell
        shell.send(command + "\n")
        # Wait for the specified interval
        time.sleep(sleep_interval_inner)
        # Receive up to 10000 bytes of data from the shell
        function_output = shell.recv(10000)
        # Decode and return the output
        return function_output.decode("utf-8")
    except Exception as e:
        # Log the exception
        logging.error(f"An error occurred while sending and receiving data: {e}")
        # Return an empty string
        return ""


# Load credentials from the file
credentials = load_credentials(args.file)

# Create an SSH client
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())


# Connect to the remote host using the credentials
try:
    ssh_client.connect(hostname=args.device, username=credentials["username"], password=credentials["password"])
    logging.info("Connection successful")
except Exception as e:
    logging.error(f"Connection failed: {e}")
    sys.exit(1)

# Get an interactive shell
ssh_shell = ssh_client.invoke_shell()

# Login to the ASA and set the CLI for further commands to be sent
output = send_and_receive(ssh_shell, 'enable\n', sleep_interval)
print(output)
output = send_and_receive(ssh_shell, f"{credentials['enable_password']} \n", sleep_interval)
print(output)
output = send_and_receive(ssh_shell, "terminal pager 0", sleep_interval)
print(output)

# Send the commands and wait for the output
for command in args.command:
    output = send_and_receive(ssh_shell, command, sleep_interval)
    print(output)

asa_cli_commands = ["show interface GigabitEthernet1/2"]

for command in asa_cli_commands:
    output = send_and_receive(ssh_shell, command, sleep_interval)
    print(output)

    # Extract and save the data using regular expressions and csv module

    # Match and capture the IP address
    ip_address = re.search(r"IP address (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", output).group(1)

    # Match and capture other data fields
    packets_input = re.search(r"(\d+) packets input", output).group(1)
    packets_output = re.search(r"(\d+) packets output", output).group(1)
    packets_dropped = re.search(r"(\d+) packets dropped", output).group(1)

    # Open or create a CSV file with append mode
    with open("asa_data.csv", "a") as file:
        # Create a csv writer object
        writer = csv.writer(file)
        # Write a header row if the file is empty
        if file.tell() == 0:
            writer.writerow(
                 ["ip_address", "packets_input", "packets_output", "packets_dropped"])
        # Write a row with the data fields
        writer.writerow([ip_address, packets_input, packets_output, packets_dropped])


# Close the SSH connection
ssh_client.close()
