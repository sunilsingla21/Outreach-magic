export FLASK_APP=app
export FLASK_DEBUG=1

. ./env/bin/activate
pip install -r requirements.txt

npm install
npm run build

flask run --host 0.0.0.0 --port 5000 --cert=adhoc
