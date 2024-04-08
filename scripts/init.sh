DEBIAN_FRONTEND=noninteractive sudo apt update
DEBIAN_FRONTEND=noninteractive sudo apt upgrade
DEBIAN_FRONTEND=noninteractive sudo apt install python3-venv
DEBIAN_FRONTEND=noninteractive sudo apt install python3-pip
cd ~/DBZ
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

