#!/bin/bash -x

echo "This is a script to setup Sivers EVK02004"

# enter RX or TX to init the board
read -p "Enter mode (TX/RX): " mode

case $mode in
    TX|tx)
        echo "Setting up TX..."
        python3 evk.py -s T582306548 -t tx_setup_24Ghz    #EVK02004 serial number: T582306549. -t: direct to test folder
        ;;
    RX|rx)
        echo "Setting up RX..."
        python3 evk.py -s T582306549 -t rx_setup_24Ghz
        ;;
    debug)
    	echo "test mode"
    	python3 evk.py -t init_test
    	;;
    *)
        echo "Invalid mode: $mode"
        echo "Please enter TX or RX."
        ;;
esac

