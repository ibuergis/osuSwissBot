# OLD: Setting up the bot to Amazon Linux
***
IMPORTANT!! THIS DID NOT WORK SINCE THERE ARE PROBLEMS WITH THE VERIFICATION VIA THE WEBSITE!!!

## Setup instance
***
We are using Amazon Linux with a space of 30Gbit

#### First connect to the instance:
````
ssh -i pathToKey ec2-user@server
````
#### Then install python3.10:
````
sudo yum install -y xz-devel
sudo yum install -y lzma
sudo yum install -y zlib-devel
sudo yum install -y gcc openssl-devel bzip2-devel libffi-devel
sudo yum install -y make
sudo yum install -y elinks

wget https://www.python.org/ftp/python/3.10.0/Python-3.10.0.tgz

tar xzf Python-3.10.0.tgz
cd Python-3.10.0  # Change to the Python source directory
./configure --enable-optimizations
make
sudo make install

cd ..
sudo rm -rf Python-3.10.0*

````

## Upload files
***
The best way is to clone it from git:
````
git clone https://github.com/ibuergis/osuSwissBot.git
````

You can update the bot with this command:
````
git pull origin master
````
## Connect to instance
***
In Terminal
````
ssh -i pathToKey ec2-user@server
````

## How to run the program
***
#### Install dependencies for the program:
````
pip3.10 install .
````

#### Use this command in the  instance
````
python3.10 main.py
````
