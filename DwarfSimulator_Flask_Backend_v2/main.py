from flask import Flask
from backend_scripts.Sign_In_Log_In.registration import registration_user
from backend_scripts.Sign_In_Log_In.authorization import authorization_user

app = Flask(__name__)

@app.route('/registrationUser', methods=['POST'])
def run_registration():
    return registration_user()

@app.route('/authorizationUser', methods=['POST'])
def run_authorization():
    return authorization_user()

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)