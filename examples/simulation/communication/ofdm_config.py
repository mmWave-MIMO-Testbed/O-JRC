# %% this module will be imported in the into your flowgraph
import numpy as np
# import matplotlib.pyplot as plt

N_tx = 4
N_ltf = N_tx
N_sc = 64

data_subcarriers = list(range(-26, -21)) + list(range(-20, -7)) + list(range(-6, 0)) + list(range(1, 7)) + list(range(8, 21)) +list( range(22, 27))
pilot_subcarriers = [-21, -7, 7, 21]
pilot_symbols = ((1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (1, 1, 1, -1), (1, 1, 1, -1), (1, 1, 1, -1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1), (-1, -1, -1, 1))

N_data = len(data_subcarriers)
N_pilot = len(pilot_subcarriers)

# l_stf_ltf_128_custom = ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (-1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 
#     (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (-1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (-1.4719601443879744-1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, (1.4719601443879744+1.4719601443879744j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 
#     (0, 0j, (-0-1j), (-0-1j), -1j, -1j, 1j, (-0-1j), -1j, 1j, 1j, (-0-1j), -1j, -1j, (-0-1j), (-0-1j), 1j, -1j, 1j, (-0-1j), 1j, 1j, (-0-1j), (-0-1j), 1j, 1j, 1j, 1j, 1j, -1j, 1j, (-0-1j), 1j, -1j, (-0-1j), 1j, 1j, -1j, (-0-1j), (-0-1j), -1j, -1j, (-0-1j), 1j, -1j, 1j, (-0-1j), (-0-1j), 1j, 1j, (-0-1j), (-0-1j), -1j, -1j, (-0-1j), (-0-1j), 1j, -1j, 1j, (-0-1j), 1j, 1j, (-0-1j), 1j, 0, (-1-0j), -1, (-1+0j), 1, (1+0j), 1, (-1+0j), -1, (1+0j), 1, (-1+0j), -1, (-1-0j), -1, (-1+0j), 1, (-1-0j), 1, (-1+0j), 1, (1+0j), -1, (-1+0j), 1, (1+0j), 1, (1+0j), 1, (-1-0j), 1, (-1+0j), 1, (-1-0j), -1, (1+0j), 1, (-1-0j), -1, (-1+0j), -1, (-1-0j), -1, (1+0j), -1, (1+0j), -1, (-1+0j), 1, (1+0j), -1, (-1+0j), -1, (-1-0j), -1, (-1+0j), 1, (-1-0j), 1, (-1+0j), -1, (-1-0j), -1, 0j), 
#     (0, 0, 1j, -1, -1j, 1, -1j, -1, -1j, -1, -1j, -1, -1j, 1, 1j, -1, 1j, 1, -1j, -1, 1j, -1, 1j, -1, 1j, -1, -1j, 1, 1j, 1, -1j, -1, 1j, 1, 1j, 1, 1j, 1, 1j, -1, -1j, 1, 1j, 1, -1j, -1, 1j, -1, 1j, -1, 1j, -1, -1j, 1, 1j, -1, 1j, 1, -1j, -1, 1j, -1, 1j, 1, 0, -1j, 1, 1j, 1, 1j, -1, 1j, -1, 1j, -1, 1j, -1, -1j, 1, 1j, 1, -1j, -1, 1j, 1, 1j, 1, 1j, 1, 1j, -1, -1j, 1, -1j, -1, 1j, 1, -1j, 1, -1j, 1, -1j, 1, 1j, -1, -1j, 1, -1j, -1, 1j, 1, 1j, 1, 1j, 1, 1j, -1, -1j, 1, 1j, 1, -1j, -1, 1j, -1, -1j, 1, 0))

# l_stf_ltf_64 = ((0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
#  (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0), 
#     (0, 0j, 0, 0j, 0, 0j, -1, 1j, -1, 1j, -1, 1j, -1, -1j, 1, 1j, 1, -1j, -1, 1j, 1, 1j, 1, 1j, 1, 1j, -1, (-0-1j), 1, -1j, -1, 1j, 0, -1j, 1, (-0-1j), 1, -1j, 1, 1j, -1, -1j, 1, (-0-1j), -1, 1j, 1, 1j, 1, 1j, 1, 1j, -1, -1j, 1, 1j, 1, -1j, -1, 0j, 0, 0j, 0, 0j), 
#     (0, 0, 0, 0, 0, 0, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 0, 1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1, 1, -1, 1, -1, 1, 1, 1, 1, 0, 0, 0, 0, 0))


l_stf_64_def = np.array([0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (-1.4719601443879746-1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, (1.4719601443879746+1.4719601443879746j), 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
l_ltf_64_def = np.array([0, 0, 0, 0, 0, 0, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 0, 1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1, 1, -1, 1, -1, 1, 1, 1, 1, 0, 0, 0, 0, 0])


l_ltf_64_custom = np.array([0, 0, 0, 0, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 0, 1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1, 1, -1, 1, -1, 1, 1, 1, 1, -1, -1, 0, 0, 0])

assert(len(l_stf_64_def) == N_sc)
assert(len(l_ltf_64_def) == N_sc)
assert(len(l_ltf_64_custom) == N_sc)


symbol_rotation = np.array([1, -1j, -1, 1j] * 16)
l_ltf_64_rot = symbol_rotation*l_ltf_64_custom
l_stf_ltf_64 = np.vstack((l_stf_64_def, l_stf_64_def, l_ltf_64_rot, l_ltf_64_custom))

# MATLAB
# [ltfLeft, ltfRight] = wlan.internal.lltfSequence()
# [zeros(4,1); 1; 1; ltfLeft; 0; ltfRight;-1;-1; zeros(3,1)];
ltf_64 = np.array([0, 0, 0, 0, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 1, 1, -1, -1, 1, 1, -1, 1, -1, 1, 1, 1, 1, 0, 1, -1, -1, 1, 1, -1, 1, -1, 1, -1, -1, -1, -1, -1, 1, 1, -1, -1, 1, -1, 1, -1, 1, 1, 1, 1, -1, -1, 0, 0, 0], dtype=np.complex64)
P_ltf = np.array([[1, -1, 1, 1], [1, 1, -1, 1], [1, 1, 1, -1], [-1, 1, 1, 1]], dtype=np.complex64)


ltf_tx = []
for i_tx in range(N_tx):
    ltf_tx.append(tuple(map(tuple, np.outer(P_ltf[i_tx,:N_ltf],ltf_64))))


ltf_mapped_64 = []
for i_tx in range(N_tx):
    ltf_expand_time = np.outer(P_ltf[i_tx,:N_ltf], ltf_64)
    ltf_mapped_64.append(ltf_expand_time.flatten().tolist())

# ltf_mapped_64 = np.array(ltf_mapped_64).T
ltf_mapped_64 = np.array(ltf_mapped_64)


# Nsc X (Ntx.Nltf) [ second dimension is row-major of (Ntx X Nltf) ]
ltf_mapped_sc__ss_sym = []
for i_sc in range(N_sc):
    ltf_ss_sym = P_ltf[:N_tx,:N_ltf]*ltf_64[i_sc]
    ltf_mapped_sc__ss_sym.append(ltf_ss_sym.flatten().tolist()) # --> flatten() follows row-major order

ltf_mapped_sc__ss_sym = np.array(ltf_mapped_sc__ss_sym)

# %%
l_ltf = l_stf_ltf_64[3]
l_ltf_time = N_sc*np.fft.ifft(np.fft.fftshift(l_ltf)) / np.sqrt(np.count_nonzero(l_ltf))
l_ltf_fir = np.conj(l_ltf_time)
l_ltf_fir = l_ltf_fir[::-1]

# plt.figure()
# plt.plot(np.abs(l_ltf_time))

# plt.figure()
# plt.plot(np.abs(np.convolve(l_ltf_fir,l_ltf_time,'full')))

# %%
