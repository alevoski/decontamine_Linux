# Decontamine_Linux
[![License](https://img.shields.io/badge/licence-AGPLv3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.en.html)
[![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)](https://www.linux.com/)
[![Language](https://img.shields.io/badge/language-python3-orange.svg)](https://www.python.org/)

Decontamine_Linux is an USB devices cleaning station for Linux.  
Started since September 2018.  
Coding and testing on ***Debian 9*** 64 bits with Python 3.  
Project ongoing.  

## Getting Started
Download the project on your computer.
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
pip install -r requirements.txt
```
#### Install at least one of this antivirus:
***ClamAV***
```
apt-get update
apt-get install clamav
apt-get install clamav-daemon
```
***Sophos***  
Download it on [Sophos website](https://www.sophos.com/en-us/products/free-tools/sophos-antivirus-for-linux.aspx)  
Install it without live protection  
```
tar -xzvf sav-linux-free-9.tgz
sudo ./sophos-av/install.sh --live-protection=false
```

### HOW TO USE ?
```
cd CS/
python3 main.py
```

## Documentation
For more information, please read the [documentation](https://github.com/alevoski/decontamine_Linux/tree/master/DOCS) in DOCS/ directory

## Author
Alexandre Buissé

## License
Decontamine_Linux. USB devices cleaning station.  
Copyright (C) 2018 Alexandre Buissé alexandre.buisse@gmail.com  

This program is free software: you can redistribute it and/or modify  
it under the terms of the GNU Affero General Public License as published  
by the Free Software Foundation, either version 3 of the License, or  
(at your option) any later version.  

This program is distributed in the hope that it will be useful,  
but WITHOUT ANY WARRANTY; without even the implied warranty of  
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the  
GNU Affero General Public License for more details.  

You should have received a copy of the GNU Affero General Public License  
along with this program.  If not, see <https://www.gnu.org/licenses/>.


