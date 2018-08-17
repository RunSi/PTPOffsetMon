# PTPOffsetMon

The PTPOffsetMon application is built for the Cisco NX-OS range of Data Center switches (Nexus 9000).  

## Basic Operation

The application will monitor, every two minutes the value of the PTP Offset from Master.  In the 
event that the PTP Offset from Master value falls outside the range of configured thresholds, then
a Syslog will be generated.  Default Threshold values are:-

*threshold 1*  = Between 1000 and 1999, and between -1000 and -1999

*threshold 2*  = Between 2000 and 4999, and between -2000 and -4999

*threshold 3*  = Above 5000 and above -5000

## Configuring Thresholds

n9kv1(config)# PTPOffsetMon Threshold1  ?

  <0-1000>  Upper threshold value in nanoseconds

## Showing currently configured Thresholds

n9kv1# show PTPOffsetMon values

Upper Threshold Sev 1 is set to 1000 

Lower Threshold Sev 1 is set to -1000 


Upper Threshold Sev 2 is set to 2000 

Lower Threshold Sev 2 is set to -2000 


Upper Threshold Sev 3 is set to 5000 

Lower Threshold Sev 3 is set to -5000

## Show Offset from Master

n9kv1# show PTPOffsetMon ptp offset 

The current ptp offset from master is at 0


## Syslog output example

If a threshold is met then the application will generate a syslog message, and example given below:-

2017 Nov  6 00:17:02 n9kv1 %NXSDK-1-ALERT MSG:  nxsdkapp1 [26071]  PTP VIOLATION - offset now at 0


## Running the application from BASH

The source code needs to be copied to the NXOS device and can be run from the BASH shell. If the code
is on bootflash:-

n9kv1# run bash

bash-4.2$ pwd

/bootflash/home/

bash-4.2$ cd /bootflash

bash-4.2$ nohup /isan/bin/python PTPOffsetMon.py &

*do not kill the application within BASH.  In order stop the application do so from the command line*

n9kv1#(config)PTPOffsetMon stop-event-loop

## Running the application as a Service

The advantages of running as a Service is that the application can be controlled by the operator from the NXOS
command line.  Additionally the application will be persistent and will continue to run after device reload.

The RPM file in this repository's RPM directory needs to be copied to the bootflash of the device.

Details on how to install RPM on NXOS devices can be found at the [NXSDK Github page](https://github.com/ciscodevnet/nx-sdk)
