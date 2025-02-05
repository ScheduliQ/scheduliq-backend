from flask import Flask
from flask_cors import CORS
from app.user_routes import user_api
from app.auth_routes import auth_api
from app.constraints_routes import constraints_api
from app.algorithm_routes import alg_api
from app.schedule_routes import schedule_api

app = Flask(__name__)
CORS(app)

app.register_blueprint(user_api, url_prefix='/user')
app.register_blueprint(auth_api,url_prefix='/auth')
app.register_blueprint(constraints_api, url_prefix="/constraints")
app.register_blueprint(alg_api,url_prefix='/csp')
app.register_blueprint(schedule_api, url_prefix="/schedule")

if __name__ == '__main__':
    app.run(debug=True)
