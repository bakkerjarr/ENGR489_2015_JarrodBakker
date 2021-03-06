# ENGR489_2015_JarrodBakker
This repository contains the implementation material for my 2015 ENGR489 project at Victoria University of Wellington.

## Basic details
My project builds upon the code contained within the VM image found on http://sdnhub.org/tutorials/sdn-tutorial-vm/ where the 64-bit image was chosen. To run the implementations, clone the repository to ~/ryu/ryu/"directory name here" and run Mininet and ryu-manager taking note to use OpenFlow 1.3.

At the time of download, Mininet was at its latest version (2.2.1) and did not need to be upgraded. However, instructions for upgrading Mininet can be found at http://mininet.org/download/, namely 'Option 4. Upgrading an existing Mininet Installation'. The version of Ryu on the image was 3.22 and was not upgraded. However, instruction to upgrade Ryu can be found at https://github.com/osrg/ryu/wiki/OpenFlow_Tutorial.

Open vSwitch was not updated as its version was 2.3.90. However, instructions for updating the image can be found at https://github.com/mininet/mininet/wiki/Installing-new-version-of-Open-vSwitch where the correct file of the Open vSwitch version is inserted.

The following Python module is required for interface.py to format table outputs: prettytable. Just use '$ sudo pip install prettytable' to install.

For testing the application, Scapy was used. Iperf was the first choice, however it does allow the user to specify the client port. Scapy allows the user to change the both the client and host port. As the functionality of Scapy is packaged in Python libraries, test scripts can be made with ease. Scapy 2.3.1 was used for testing. To install Scapy run the following command '$ sudo apt-get install python-scapy'. The module 'netifaces' was used to get the details of a machine's interfaces and IP addresses. To install netifaces run the following command '$ sudo pip install netifaces'.

## Directory details
###ACLSwitch
Contains the implementation code for ACLSwitch.

### Archive
Contains a collection of files from various stages of the project. It serves as a storage for draft files that can be easily accessed in the event that problems arise with later implementations.
 
WARNING: There is no guarantee that code contained in this section of the repository will work. Do not expect either working or good looking code.

###Interface
Contains the implementation code for the ACLSwith command-line interface.

###Tests
Contains the testing scripts for ACLSwitch.

##Commands for checking versions
Check Mininet version:
    $ mn --version

Check Ryu version:
    $ ~/ryu/bin/ryu-manager --version

Check Open vSwitch version:
    $ ovs-vswitchd --version

##List of Python modules that need to be installed onto the VM
- prettytable
- Scapy
- netifaces
