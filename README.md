# O-JRC: An Open Source Software Platform for mmWave Joint Radar-Communication Development and Experimentation

This project is developed and tested in Ubuntu 20.04 and Ubuntu 22.04. We recommend installing GnuRadio and UHD from source whose links are provided below. Additionally, this project uses Eigen3 library for linear algebra operations in C++.

### [Project Website](https://u.osu.edu/ekici/jrc-testbed/)

## Requirements

+ [GnuRadio v3.8.5.0](https://wiki.gnuradio.org/index.php?title=InstallingGR#For_GNU_Radio_3.8_or_Earlier) (Branch: maint-3.8)
  + [Dependencies for Ubuntu](https://wiki.gnuradio.org/index.php?title=UbuntuInstall#Focal_Fossa_(20.04)_through_Impish_Indri_(21.10))
+ [UHD v4.1.0.5](https://github.com/EttusResearch/uhd/releases/tag/v4.1.0.5)
+ [Eigen3](https://eigen.tuxfamily.org)
  + sudo apt-get install libeigen3-dev
+ [Qt5Qwt6](https://wiki.qt.io/Main) (should be installed with the dependencies of GnuRadio v3.8)
  + sudo apt-get install libqt5opengl5-dev 
+ [QWT](https://qwt.sourceforge.io/) (should be installed with the dependencies of GnuRadio v3.8)
  + sudo apt-get install libqwt-qt5-dev

## Installation

    mkdir build
    cd build
    cmake ..
    make
    sudo make install
    sudo ldconfig

## Usage

### [Packet Generator App](https://github.com/ceyhunozkaptan/mimo-ofdm-packet-generator): 
This application can be used to generate Data Packets (DATA) or Null Data Packets (NDP). It utilizes an internal UDP socket to send packets to the GnuRadio flowgraph.

### Simulation

## License

This project is licensed under the MIT License.

# Related Publications

* C. D. Ozkaptan, E. Ekici, C. -H. Wang and O. Altintas, "[Optimal Precoder Design for MIMO-OFDM-based Joint Automotive Radar-Communication Networks](https://ieeexplore.ieee.org/abstract/document/9589830/)," International Symposium on Modeling and Optimization in Mobile, Ad hoc, and Wireless Networks (WiOpt), 2021
* C. D. Ozkaptan, H. Zhu, E. Ekici, and O. Altintas, "[Software-Defined MIMO OFDM Joint Radar-Communication Platform with Fully Digital mmWave Architecture](https://arxiv.org/abs/2302.05812)," 2023 3rd IEEE International Symposium on Joint Communications & Sensing (JC&S)

