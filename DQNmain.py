import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import subprocess
from datetime import datetime
import paramiko  # Import paramiko for SSH

#this defined the initial class for the DQN system 
class DQN:
    def __init__(self, state_space, action_space):
        self.model = Sequential([
            Dense(24, input_shape=(state_space,), activation='relu'),
            Dense(24, activation='relu'),
            Dense(action_space, activation='linear')
        ])
        self.model.compile(loss='mse', optimizer=Adam(learning_rate=0.001))

    def predict(self, state):
        return self.model.predict(state)

#this used to load the DQN weight values gathered from traning process
def load_and_use_dqn_model(weights_file, utilization1, utilization2):
    state = np.array([utilization1, utilization2]).reshape(1, 2)
    agent = DQN(state_space=2, action_space=2)
    agent.model.load_weights(weights_file)

    # Use the trained model to make a decision
    action = np.argmax(agent.predict(state)[0])

    if action == 0:
        selected_link = "Link1Flow1"
    if action == 1:
        selected_link = "Link2Flow1"


    return selected_link

#this used to connect and udate remote file regarding DQN desition 
def update_remote_file(host, username, password, remote_path, new_content):
    try:
        ssh_client = paramiko.SSHClient()
  ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, username=username, password=password)

        # Open an SFTP session using SSHClient
        sftp = ssh_client.open_sftp()

        # Update the remote file
        with sftp.file(remote_path, 'w') as remote_file:
            remote_file.write(new_content)

        # Close the SFTP session
        sftp.close()

        ssh_client.close()
    except Exception as e:
        print(f"Error occured during update remote file: {str(e)}")

if __name__ == "__main__":
    num_iterations = 100  # Change this to the number of iterations you want
    selected_link = None  # Initialize selected_link variable

    for iteration in range(num_iterations):
        # Run link1_status.py to get utilization1
        utilization1_output = subprocess.check_output(["python", "link1_status.py"]).decode("utf-8")
        utilization1 = float(utilization1_output.strip())

        # Run link2_status.py to get utilization2
        utilization2_output = subprocess.check_output(["python", "link2_status.py"]).decode("utf-8")
        utilization2 = float(utilization2_output.strip())



        # Load weights from the corresponding episode file
        episode_weights_file = f'trained_model_weights_episode_{iteration + 1}.h5'
        new_selected_link = load_and_use_dqn_model(episode_weights_file, utilization1, utilization2)

        print(f"Utilization of Link 1: {utilization1}")
        print(f"Utilization of Link 2: {utilization2}")

        print(f"Traffic flowing through: {new_selected_link}")
        # Check if the selected link has changed
        if selected_link != new_selected_link:
            selected_link = new_selected_link

            # ssh connection for SDN SR network
            host = "192.168.44.137"
            username = "mininet"
            password = "mininet"
            remote_path = "/home/mininet/onos/modify.txt"
            new_content = ""

            # Update the SDN SR network
            if new_selected_link == "link1flow1":
                new_content = "link1flow1"
            elif new_selected_link == "link2flow1":
                new_content = "link2flow1"

            # Update the remote file
            update_remote_file(host, username, password, remote_path, new_content)

