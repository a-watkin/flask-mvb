import subprocess
from flask import Flask
from blog.post_routes import post_blueprint

app = Flask(__name__)

app.config.update(
    TESTING=True,
    SECRET_KEY='whyohwhy'
)

app.register_blueprint(post_blueprint, url_prefix="/posts")


@app.route('/')
def hello_world():
    return 'sure does!'


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

    app.run(
        debug=True,
        port=5050
    )
