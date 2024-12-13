from flask import Flask
from flask_cors import CORS
from app.routes import api

app = Flask(__name__)
CORS(app)

app.register_blueprint(api, url_prefix='/')



if __name__ == '__main__':
    app.run(debug=True)
