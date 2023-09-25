import subprocess

# Define the remote server's details
username = "mininet"
password = "mininet"
remote_ip = "192.168.44.137"

# Define the shell command as a list of arguments
command = [
    "sshpass",
    "-p", password,
    "ssh",
    "-v",  
    f"{username}@{remote_ip}",
    "bash",  # Specify the shell to execute the command
    "-c",    # Use -c to provide the command as a string
    'echo -n "leaf1-eth2: "; ifstat -i leaf1-eth2 -q 1 1 | awk \'NR == 3 {gsub(".*: ", "", $0); printf("%.2f", ($2 / 10))}\''
]

try:
    # Execute the shell command
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"Command failed with error code {e.returncode}")
    print(e.stderr)
except Exception as e:
    print(f"An error occurred: {e}")

~                                                                                                                                                                                                           
~                                
