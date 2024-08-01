import numpy as np
#import matplotlib.pyplot as plt

N_tx = 1  
N_ltf = N_tx
N_sc = 16 

data_subcarriers = list(range(-7, -4)) + list(range(-3, 0)) + list(range(0, 4)) + list(range(5, 8))
pilot_subcarriers = [-4, 4]

N_data = len(data_subcarriers)
N_pilot = len(pilot_subcarriers)

pilot_symbols = [(1, 1), (1, 1), (1, 1), (1, 1), 
                 (-1, -1), (-1, -1), (-1, -1), (-1, -1), 
                 (1, 1), (1, 1), (1, 1), (1, 1), 
                 (-1, -1), (-1, -1), (-1, -1), (-1, -1)]

l_stf_16_def = np.array([0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, (1.4719601443879746+1.4719601443879746j)])
l_ltf_16_def = np.array([0, 0, 1, 1, -1, 1, 1, 1, -1, 1, -1, 1, 1, -1, -1, 0])

l_ltf_16_custom = np.array([0, 1, 1, -1, 1, 1, -1, 1, -1, 1, 1, -1, -1, 1, 1, 0])

assert(len(l_stf_16_def) == N_sc)
assert(len(l_ltf_16_def) == N_sc)
assert(len(l_ltf_16_custom) == N_sc)

symbol_rotation = np.array([1, -1j, -1, 1j] * 4)
l_ltf_16_rot = symbol_rotation * l_ltf_16_custom
l_stf_ltf_16 = np.vstack((l_stf_16_def, l_stf_16_def, l_ltf_16_rot, l_ltf_16_custom))

ltf_16 = np.array([0, 1, 1, -1, 1, 1, -1, 1, -1, 1, 1, -1, -1, 1, 1, 0], dtype=np.complex64)
P_ltf = np.array([[1, -1, 1, 1]], dtype=np.complex64)

ltf_tx = []
for i_tx in range(N_tx):
    ltf_tx.append(tuple(map(tuple, np.outer(P_ltf[i_tx, :N_ltf], ltf_16))))

ltf_mapped_16 = []
for i_tx in range(N_tx):
    ltf_expand_time = np.outer(P_ltf[i_tx, :N_ltf], ltf_16)
    ltf_mapped_16.append(ltf_expand_time.flatten().tolist())

ltf_mapped_16 = np.array(ltf_mapped_16)

ltf_mapped_sc__ss_sym = []
for i_sc in range(N_sc):
    ltf_ss_sym = P_ltf[:N_tx, :N_ltf] * ltf_16[i_sc]
    ltf_mapped_sc__ss_sym.append(ltf_ss_sym.flatten().tolist())

ltf_mapped_sc__ss_sym = np.array(ltf_mapped_sc__ss_sym)

# %%
l_ltf = l_stf_ltf_16[3]
l_ltf_time = N_sc * np.fft.ifft(np.fft.fftshift(l_ltf)) / np.sqrt(np.count_nonzero(l_ltf))
l_ltf_fir = np.conj(l_ltf_time)
l_ltf_fir = l_ltf_fir[::-1]

#plt.figure()
#plt.plot(np.abs(l_ltf_time))

#plt.figure()
#plt.plot(np.abs(np.convolve(l_ltf_fir, l_ltf_time, 'full')))

