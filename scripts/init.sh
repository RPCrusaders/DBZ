# for the love of all that is good please just run the script in project dir
if [ "$(pwd)" == "$HOME/PycharmProjects/DBZ/scripts" ]; then
  cd ..
fi

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
