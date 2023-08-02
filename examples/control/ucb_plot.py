import matplotlib.pyplot as plt
import numpy as np
ucb_mean_info = np.loadtxt("ucb_mean_info.csv", delimiter=",")
ucb_info = np.loadtxt("ucb_info.csv", delimiter=",")
#context_values = np.arange(-90,90,1)
context_values = np.arange(22,23,1)
for context in context_values:
    ucb_mean = ucb_mean_info[context+90,:]
    ucb_estimates = ucb_info[context+90,:]
    plt.plot(range(-90, 91), ucb_mean, label=f'radar angle{context}')
    plt.plot(range(-90, 91), ucb_estimates, label=f'radar angle{context}')

plt.xlabel('Beamforming angle')
plt.ylabel('UCB Estimate')
plt.title('UCB Estimates for Different Radar angle')
plt.legend()
plt.show()