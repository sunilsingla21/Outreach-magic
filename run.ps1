# Set environment variables
$env:FLASK_APP = "app"
$env:FLASK_DEBUG = "1"

# Activate virtual environment
. .\env\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Execute npm commands
npm install
npm run build

# Run flask
flask run --host 0.0.0.0 --port 5000 --cert=adhoc
