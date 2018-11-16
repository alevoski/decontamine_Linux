# Decontamine_Linux
[![License](https://img.shields.io/badge/licence-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.en.html)
[![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)](https://www.linux.com/)
[![Language](https://img.shields.io/badge/language-python3-orange.svg)](https://www.python.org/)
[![LinkedIn](https://img.shields.io/badge/linkedIn-https%3A%2F%2Fwww.linkedin.com%2Fin%2Falexandre--buisse%2F-blue.svg)](https://www.linkedin.com/in/alexandre-buisse/)

Decontamine_Linux is an USB devices cleaning station for Linux
Started since September 2018
Coding and testing on Debian 9 64 bits with Python 3
Project ongoing

## Getting Started
Download the project on your computer
```
git clone https://github.com/alevoski/decontamine_Linux.git
```

### Prerequisites
#### Create a user "decontamine" or a folder named "decontamine" in /home
Put the folder writing permission for anyone.
It's where  the logs files and the config file will be stored.
```
sudo chmod -R 757 /home/decontamine
```

#### Install the required pip modules
```
***ONGOING***
```
#### Install at list one this antivirus:
ClamAV
```
apt-get update
apt-get install clamav
apt-get install clamav-daemon
```
Sophos
```
Download on https://www.sophos.com/en-us/products/free-tools/sophos-antivirus-for-linux.aspx
Install it without live protection
tar -xzvf sav-linux-free-9.tgz
sudo ./sophos-av/install.sh --live-protection=false
```

### HOW TO USE ?
```
cd CS/
python3 main.py
```

## Documentation
For more information, please read the [documentation] (https://github.com/alevoski/decontamine_Linux/tree/master/DOCS) in DOCS/ directory

## Author
Alexandre Buissé

## License
<iframe src="https://github.com/alevoski/decontamine_Linux/blob/master/LICENSE"></iframe> 

