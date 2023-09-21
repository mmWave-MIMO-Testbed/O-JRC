import numpy as np
import CMAB_algorithm
import os

# 获取脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'raw_data_ES.csv')

# 使用 np.loadtxt 读取文件
raw_data = np.loadtxt(file_path, delimiter=',', usecols=(1,2,3,4), skiprows=1)

#filename = "raw_data_ES.csv"

n_radar_angle = 181 # one degree resolution
n_beamforming_angle = 121 # one degree resolution
agent = CMAB_algorithm.ContextualUCB(n_radar_angle,n_beamforming_angle)

# 使用 np.loadtxt 读取 csv 文件。skiprows=1用来跳过文件的第一行（标题行）
#raw_data = np.loadtxt(filename, delimiter=',', usecols=(1,2,3,4), skiprows=1)

#Load trained model if needed
trained_model_mean = np.load('estimated_mean.npy')
trained_total_play = np.load('total_play.npy')
trained_action_play = np.load('context_action_play.npy')
agent.load_trained_model(trained_model_mean, trained_total_play, trained_action_play)

print("Load ES raw data")
# 对读取的每一行进行操作
for row in raw_data:
    curr_radar_angle, curr_beamforming_angle, curr_comm_snr, curr_comm_reward = row
    
    curr_radar_angle = int(np.round(curr_radar_angle))
    curr_beamforming_angle = int(np.round(curr_beamforming_angle))
    # 计算 reward
    reward = curr_comm_reward * (1 / (1 + (np.exp(-0.8 * (curr_comm_snr - 20)))))
    
    # 更新 agent
    agent.update(curr_radar_angle + 90, curr_beamforming_angle + 60, reward)

print("Finish training")
agent.save_trained_model()
trained_model_mean = np.load('estimated_mean.npy')
print(f"Trained model: {trained_model_mean}")

