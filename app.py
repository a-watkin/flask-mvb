from user.user_routes import user_blueprint
from blog.post_routes import post_blueprint
from tag.tag_routes import tag_blueprint
import os
import subprocess
from flask import Flask, render_template

DEVELOPMENT = True


app = Flask(__name__)

app.register_blueprint(post_blueprint,
                       url_prefix="/posts")

app.register_blueprint(user_blueprint, url_prefix="/user")
app.register_blueprint(tag_blueprint, url_prefix="/tag")


app.config.update(
    TESTING=True,
    SECRET_KEY='testing'
    # SECRET_KEY=os.urandom(16)

)


@app.route('/', methods=['GET'])
def test():
    return render_template('home.html')


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

    # app.run(
    #     debug=True,
    #     host='0.0.0.0'
    # )

    if DEVELOPMENT:
        app.run(
            debug=True,
            port=5050
        )
    else:
        app.run(
            debug=False,
            host='0.0.0.0'
        )
