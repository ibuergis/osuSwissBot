# Setup the bot
***
Here I will explain everything needed for the bot

## Upload files
***
Run this command in Windows

````
scp -i pathToKey -r pathToProject ec2-user@server:
````
## Connect to instance
***
In Terminal
````
ssh -i pathToKey ec2-user@server
````

## How to run the program
***
use this command in the  instance
````
python3.10 main.py
````

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

#### And lastly install dependencies for the program:
````
pip -m pip install .
````