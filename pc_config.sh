#!/bin/bash -x 
echo "This is a script to tune the HostPC"  

# INCREASES BUFFER SIZES
echo 12451245 | sudo sysctl -w net.core.rmem_max=33554432 #50000000 #33554432
echo 12451245 | sudo sysctl -w net.core.rmem_default=33554432
echo 12451245 | sudo sysctl -w net.core.wmem_max=33554432
echo 12451245 | sudo sysctl -w net.core.wmem_default=33554432
echo 12451245 | sudo sysctl -w net.core.optmem_max=25165824 
echo 12451245 | sudo sysctl -w net.core.netdev_max_backlog=300000 #65536 

# SETS CPUs GOVERNOR TO PERFORMANCE
for ((i=0;i<$(nproc);i++)); do echo 12451245 | sudo cpufreq-set -c $i -r -g performance; done
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# STOPS IRQ BALANCING SERVICE
echo 12451245 | sudo systemctl stop irqbalance.service

# CHANGES PCI-X Command Register for INTEL X520 
# http://dak1n1.com/blog/7-performance-tuning-intel-10gbe/
echo 12451245 | sudo setpci -v -d 8086:10fb e6.b=2e


# SETS BUFFERS OF 10Gbps Ethernet NICs
#echo 12451245 | sudo -S ethtool -G enp8s0f0 tx 4096 rx 4096 
#echo 12451245 | sudo -S ethtool -G enp8s0f1 tx 4096 rx 4096
echo 12451245 | sudo -S ethtool -G enp9s0f0 tx 4096 rx 4096
echo 12451245 | sudo -S ethtool -G enp9s0f1 tx 4096 rx 4096
#echo 12451245 | sudo -S ethtool -G enp1s0f0 tx 4096 rx 4096
echo 12451245 | sudo -S ethtool -G enp1s0f1 tx 4096 rx 4096
echo 12451245 | sudo -S ethtool -C enp9s0f0 rx-usecs 1
echo 12451245 | sudo -S ethtool -C enp9s0f1 rx-usecs 1
#echo 12451245 | sudo -S ethtool -C enp1s0f0 rx-usecs 1
echo 12451245 | sudo -S ethtool -C enp1s0f1 rx-usecs 1

#default rx-usecs 1 --> Adaptive
#default tx rx 512


