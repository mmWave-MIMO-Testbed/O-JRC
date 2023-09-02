import numpy as np
# In[26]:

class ContextualUCB:
    def __init__(self, n_radar_angle, n_beamforming_angle):
        # n_radar_angle: is the total number of angles which can be read from radar (depend on resolution)
        # n_beamformnig_angle: is the total number of angles which will apply to stream encoder  
        self.n_contexts = n_radar_angle
        self.n_actions = n_beamforming_angle
        self.total_plays = np.ones(n_radar_angle)
        self.context_action_counts = np.zeros((n_radar_angle, n_beamforming_angle))
        self.context_action_estimates = np.zeros((n_radar_angle, n_beamforming_angle))

    def get_ucb_value(self, radar_angle):
        ucb_value = self.context_action_estimates[radar_angle, :] + \
                        0.5* np.sqrt(2 * np.log(self.total_plays[radar_angle]) / (1 + self.context_action_counts[radar_angle, :]))
        return ucb_value
    
    def get_mean_value(self,radar_angle):
        mean_value = self.context_action_estimates[radar_angle,:]
        return mean_value

    def angle_selection(self, radar_angle):
        ucb_value = self.get_ucb_value(radar_angle)
        return np.argmax(ucb_value) - 90 # - 90 to change the range of angle to (-90,90) 

    def update(self, radar_angle, beamforming_angle, reward):
        self.total_plays[radar_angle] += 1
        self.context_action_counts[radar_angle, beamforming_angle] += 1 # increment the time of plays
        q_n = self.context_action_estimates[radar_angle, beamforming_angle] # calculate Q(t)value
        n = self.context_action_counts[radar_angle, beamforming_angle] # calculate number of times the arm is played
        self.context_action_estimates[radar_angle, beamforming_angle] += (reward - q_n) / n # update the UCB value
        
    def save_mean_info(self):
        np.savetxt("ucb_mean_info.csv",self.context_action_estimates,delimiter=',')

    def save_ucb_info(self):
        for angle in np.arange(0,self.n_contexts,1):
            if angle == 0:
                ucb_info_value = self.get_mean_value(angle)
            else:
                ucb_new = self.get_ucb_value(angle)
                ucb_info_value = np.vstack((ucb_info_value,ucb_new))
        np.savetxt("ucb_info.csv",ucb_info_value,delimiter=',')

    def save_trained_model(self):
        np.save('estimated_mean.npy',self.context_action_estimates)
        np.save('total_play.npy',self.total_plays)
        np.save('context_action_play.npy',self.context_action_counts)

    def load_trained_model(self, est_mean, total_play, context_action_play):
        self.context_action_estimates = est_mean
        self.total_plays = total_play
        self.context_action_counts = context_action_play

