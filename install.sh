sudo apt update -y


sudo apt install minicom -y

sudo apt install virtualenv -y

sudo apt install ssh -y

sudo apt install python3-pip -y

sudo mkdir /client/
sudo chown vvdn:vvdn /client/

cd /client/

virtualenv -p python3 venv

source venv/bin/activate

pip install pyserial pyyaml easygui pymsgbox python-dateutil

sudo apt install python3-tk -y

