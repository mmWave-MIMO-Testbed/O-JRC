import matplotlib.pyplot as plt
import numpy as np
ucb_info = np.loadtxt("ucb_info.csv", delimiter=",")
#context_values = np.arange(-90,90,1)
context_values = np.arange(0,20,1)
for context in context_values:
    ucb_estimates = ucb_info[context,:]
    plt.plot(range(-90, 91), ucb_estimates, label=f'radar angle{context}')

plt.xlabel('Beamforming angle')
plt.ylabel('UCB Estimate')
plt.title('UCB Estimates for Different Radar angle')
plt.legend()
plt.show()