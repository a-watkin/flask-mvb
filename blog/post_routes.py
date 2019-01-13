
from flask import Blueprint, jsonify, request, render_template, redirect, url_for
from .post import Post

post_blueprint = Blueprint('posts', __name__)


@post_blueprint.route('/', methods=['GET'])
def get_posts():
    p = Post()
    posts = p.get_posts()
    return render_template('posts.html', posts=posts), 200


@post_blueprint.route('/new', methods=['GET', 'POST'])
def create_post():

    if request.method == 'GET':
        return render_template('new_post.html'), 200
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        print('title ', title, '\n', 'content ', content)
        p = Post(title=title, content=content)
        print(p)
        p.create_post()

        if p.get_post(p.post_id):
            # redirect doesn't work here for some reason
            return get_posts()
        else:
            return 'Oh no something went wrong :('
