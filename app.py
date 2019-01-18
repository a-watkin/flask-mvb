import os
import subprocess
from flask import Flask

DEVELOPMENT = True

from blog.post_routes import post_blueprint
from blog.user_routes import user_blueprint

app = Flask(__name__)

app.register_blueprint(post_blueprint, url_prefix="/posts")
app.register_blueprint(user_blueprint, url_prefix="/user")


app.config.update(
    TESTING=True,
    SECRET_KEY=os.urandom(16)
)


@app.route('/', methods=['GET'])
def test():
    return 'getting here?'


if __name__ == '__main__':
    export_settings = [
        "export FLASK_APP=app.py",
        "export FLASK_ENV=development",
        "export FLASK_DEBUG=1"
    ]

    for command in export_settings:
        print(command.split())
        process = subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            shell=True
        )


    if DEVELOPMENT:
        app.run(
            debug=True,
            port=5000
        )
    else:
        app.run(
            debug=False,
            host='0.0.0.0'
        )

