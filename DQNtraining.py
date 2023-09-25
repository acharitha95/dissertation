#Libraries used for the programme
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
import subprocess
import paramiko  # for SSH

#class created for DQN system
class DQN:
    def __init__(self, state_space, action_space):
        self.model = Sequential([
            Dense(24, input_shape=(state_space,), activation='relu'),
            Dense(24, activation='relu'),
            Dense(action_space, activation='linear')
        ])
        self.model.compile(loss='mse', optimizer=Adam(lr=0.001))

#train function
    def train(self, state, target):
        self.model.fit(state, target, epochs=1, verbose=0)

#train predict
    def predict(self, state):
        return self.model.predict(state)

# update the remote file function
def update_remote_file(host, username, password, remote_path, new_content):
    try:
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_client.connect(host, username=username, password=password)


        with ssh_client.open_sftp().file(remote_path, 'w') as remote_file:
            remote_file.write(new_content)

        ssh_client.close()
    except Exception as e:
        print(f"Error updating remote file: {e}")

def train_dqn_agent(utilization1, utilization2, max_episodes):
    agent = DQN(state_space=2, action_space=2)
    gamma = 0.99

selected_action = None

    for episode in range(max_episodes):
        print(f"Episode {episode + 1}")
        total_reward = 0
        state = np.array([utilization1, utilization2]).reshape(1, 2)

        action = np.argmax(agent.predict(state)[0])

        # Check if the values is changed
        if selected_action != action:
            selected_action = action

            #SSH connection details
            host = "192.168.44.137"
            username = "mininet"
            password = "mininet"
            remote_path = "/home/mininet/onos/modify.txt"

            # Update the remote file based on desition
            if action == 0:
                new_content = "link1flow1"  # Modify this as needed
            elif action == 1:
                new_content = "link2flow1"  # Modify this as needed

            # Update the remote file command
            update_remote_file(host, username, password, remote_path, new_content)

        # Update the state 
        next_utilization1_output = subprocess.check_output(["python", "link1_status.py"]).decode("utf-8")
        next_utilization1 = float(next_utilization1_output.strip())

        next_utilization2_output = subprocess.check_output(["python", "link2_status.py"]).decode("utf-8")
        next_utilization2 = float(next_utilization2_output.strip())

        next_state = np.array([next_utilization1, next_utilization2]).reshape(1, 2)

        # Define the reward method
        if action == 0:
            reward = 1
        else:
            reward = 0
        if next_utilization1 > 50:
            reward = -0.5  # Apply a low reward for high utilization occured

        total_reward += reward
        state = next_state

        target = reward + gamma * np.amax(agent.predict(next_state))
        target_f = agent.predict(state)
        target_f[0][action] = target
        agent.train(state, target_f)

        agent.model.save_weights(f'trained_model_weights_episode_{episode + 1}.h5')
        print(f"Episode: {episode + 1}, Total Reward: {total_reward}")
        print("Model saved at episode", episode + 1)

if __name__ == "__main__":
    max_episodes = 500

    utilization1_output = subprocess.check_output(["python", "link1_status.py"]).decode("utf-8")
    utilization1 = float(utilization1_output.strip())

    utilization2_output = subprocess.check_output(["python", "link2_status.py"]).decode("utf-8")
    utilization2 = float(utilization2_output.strip())

    train_dqn_agent(utilization1, utilization2, max_episodes)

    print("Training completed for", max_episodes, "episodes.")
