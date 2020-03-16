echo "Installing APT packages.."
sudo apt install python3.8 python3.8-venv

echo "Creating venv.."
virtualenv --python=/usr/bin/python3.8 --no-site-packages --distribute .venv

echo "Sourcing venv.."
source .venv/bin/activate

echo "Installing packages.."
pip install -r requirements.txt
