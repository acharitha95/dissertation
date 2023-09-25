import subprocess

# Remote SDN network server's details
username = "mininet"
password = "mininet"
remote_ip = "192.168.44.137"

# Arguments
command = [
    "sshpass",
    "-p", password,
    "ssh",
    "-v",
    f"{username}@{remote_ip}",
    "bash",
    "-c",
    'echo -n "leaf1-eth1: "; ifstat -i leaf1-eth1 -q 1 1 | awk \'NR == 3 {gsub(".*: ", "", $0); printf("%.2f", ($2 / 10))}\''
]

try:
    # run the shell command
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print(f"Command not worked and error  code is {e.returncode}")
    print(e.stderr)
except Exception as e:
    print(f"Error occurred: {e}")
