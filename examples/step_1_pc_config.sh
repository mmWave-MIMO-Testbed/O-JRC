#!/bin/bash -x 
echo "This is a script to tune the HostPC"  

# INCREASES BUFFER SIZES
echo 7125 | sudo sysctl -w net.core.rmem_max=33554432 #50000000 #33554432
echo 7125 | sudo sysctl -w net.core.rmem_default=33554432
echo 7125 | sudo sysctl -w net.core.wmem_max=33554432
echo 7125 | sudo sysctl -w net.core.wmem_default=33554432
echo 7125 | sudo sysctl -w net.core.optmem_max=25165824 
echo 7125 | sudo sysctl -w net.core.netdev_max_backlog=300000 #65536 

# SETS CPUs GOVERNOR TO PERFORMANCE
for ((i=0;i<$(nproc);i++)); do echo performance | sudo tee /sys/devices/system/cpu/cpu$i/cpufreq/scaling_governor; done
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor


# STOPS IRQ BALANCING SERVICE
echo 7125 | sudo systemctl stop irqbalance.service


#default rx-usecs 1 --> Adaptive
#default tx rx 512