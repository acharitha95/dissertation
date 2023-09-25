import subprocess
import time

# Define the modify values
current_modified_value = None

# Function to run ONOS commands
def run_onos_command(command):
    try:
        subprocess.check_call(command, shell=True)
        print('Successfully applied the  Policy to SDN : ' + command)
    except subprocess.CalledProcessError as e:
        print('Error applying policy: ' + command)
        print(e)

# Main loop to check modify file change
while True:
    with open('/home/mininet/onos/modify.txt', 'r') as modify_file:
        modify_value = modify_file.read().strip()

    # Check if modify_value change
    if modify_value != current_modified_value:
        current_modified_value = modify_value

        if modify_value == "link1flow1":
            # Run policies


            run_onos_command('onos-batch 10.0.3.215 "srpolicy-add p1 1001 10.0.1.1/24 0 10.0.2.2/24 49152 TCP TUNNEL_FLOW FASTPATH"')
            run_onos_command('onos-batch 10.0.3.215 "srpolicy-remove p2"')

        elif modify_value == "link2flow1":
            # Run policies
            run_onos_command('onos-batch 10.0.3.215 "srpolicy-add p2 1002 10.0.1.1/24 0 10.0.2.2/24 49152 TCP TUNNEL_FLOW SLOWPATH"')
            run_onos_command('onos-batch 10.0.3.215 "srpolicy-remove p1"')

    # Sleep for a second. This can change according to requirement
    time.sleep(1)
