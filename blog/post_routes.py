
from flask import Blueprint, jsonify, request, render_template
from .post import Post

post_blueprint = Blueprint('posts', __name__)


@post_blueprint.route('/', methods=['GET'])
def get_posts():
    p = Post()
    posts = p.get_posts()
    return render_template('posts.html', posts=posts), 200
