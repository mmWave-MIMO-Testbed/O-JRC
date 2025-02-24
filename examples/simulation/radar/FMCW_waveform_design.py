import numpy as np
import matplotlib.pyplot as plt
import os

# 参数设置
sweep_time = 1e-5      # 扫频时长 1 μs
bandwidth  = 62.5e6     # 带宽 125 MHz
fs = 125e6             # 采样率 250 MHz（建议至少为2倍带宽）

# 生成时间序列
t = np.arange(0, sweep_time, 1/fs)

# 计算chirp速率 k (Hz/s)
k = bandwidth / sweep_time

# 计算累积相位，基带信号（f0=0）
phase = 2 * np.pi * (0 * t + 0.5 * k * t**2)

# 生成复数信号（IQ），FMCW 波形
fmcw_wave = np.exp(1j * phase)

# create long FMCW Waveform
repeat_factor =10
long_fmcw_wave = np.tile(fmcw_wave, repeat_factor)
# ----- 绘图 -----

plt.figure(figsize=(12, 10))

# 1. 时域波形：绘制实部和虚部
plt.subplot(3, 1, 1)
plt.plot(t, fmcw_wave.real, label='Real')
plt.plot(t, fmcw_wave.imag, label='Image')
plt.xlabel("s")
plt.ylabel("Amplitude")
plt.title("FMCW Waveform")
plt.legend()
plt.grid(True)

# 2. 瞬时频率：通过对unwrap后的相位求导计算
inst_phase = np.unwrap(np.angle(fmcw_wave))
inst_freq = np.diff(inst_phase) / (2 * np.pi) * fs
plt.subplot(3, 1, 2)
plt.plot(t[1:], inst_freq, color='r')
plt.xlabel("s")
plt.ylabel("Hz")
plt.title("FMCW instantaneous frequency")
plt.grid(True)

# 3. 频域图：FFT变换并绘制频谱（幅度）
N = len(fmcw_wave)
f = np.linspace(-fs/2, fs/2, N)
F = np.fft.fftshift(np.fft.fft(fmcw_wave, n=N))
F_mag = np.abs(F)
plt.subplot(3, 1, 3)
plt.plot(f, F_mag, color='g')
plt.xlabel("Hz")
plt.ylabel("Amplitude")
plt.title("FMCW frequency response")
plt.grid(True)

plt.tight_layout()
plt.show()

# 获取当前脚本所在的目录
script_dir = os.path.dirname(os.path.abspath(__file__))
dat_file = os.path.join(script_dir, "fmcw_chirp.dat")
long_dat_file = os.path.join(script_dir, "fmcw_chirpLong.dat")

# 将数据保存为 complex64 格式的二进制文件到脚本所在目录
fmcw_wave.astype(np.complex64).tofile(dat_file)
long_fmcw_wave.astype(np.complex64).tofile(long_dat_file)

print(f"FMCW 波形已保存到: {dat_file}")