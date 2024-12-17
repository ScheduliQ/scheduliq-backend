from flask import Flask
from flask_cors import CORS
from app.user_routes import user_api
from app.auth_routes import auth_api


app = Flask(__name__)
CORS(app)

app.register_blueprint(user_api, url_prefix='/user')
app.register_blueprint(auth_api,url_prefix='/auth')


if __name__ == '__main__':
    app.run(debug=True)
