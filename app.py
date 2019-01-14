import subprocess
from flask import Flask
# this only sort of works
# from flaskext.markdown import Markdown

from blog.post_routes import post_blueprint
from blog.user_routes import user_blueprint

app = Flask(__name__)
# Markdown(app)

# template_folder='blog/templates',
# static_folder = 'blog/static'

app.register_blueprint(post_blueprint, url_prefix="/posts")
app.register_blueprint(user_blueprint, url_prefix="/user")

app.config.update(
    TESTING=True,
    SECRET_KEY='whyohwhy'
)

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
