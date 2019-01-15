
from flask import Blueprint, jsonify, request, render_template, redirect, url_for

import mistune
from .post import Post

post_blueprint = Blueprint('posts', __name__)


@post_blueprint.route('/', methods=['GET'])
def get_posts():
    p = Post()
    posts = p.get_posts()
    markdown = mistune.Markdown()
    for post in posts:
        post['content'] = markdown(post['content'])
    return render_template('posts.html', posts=posts), 200


@post_blueprint.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    p = Post()
    post = p.get_post(post_id)
    if post:
        markdown = mistune.Markdown()
        post[0]['content'] = markdown(post[0]['content'])
    return render_template('post.html', post=post), 200


@post_blueprint.route('/new/', methods=['GET', 'POST'])
def create_post():
    print('hello from create post ')
    if request.method == 'GET':
        return render_template('new_post.html'), 200
    if request.method == 'POST':
        # get the values
        title = request.form['title']
        content = request.form['content']
        # make the psot
        p = Post(title=title, content=content)
        p.create_post()

        if p.get_post(p.post_id):
            # if you have a status code here it doesn't redirect
            return redirect(url_for('posts.get_posts'))
        else:
            return 'Oh no something went wrong :(', 404


@post_blueprint.route('/edit/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    if request.method == 'GET':
        p = Post()
        post = p.get_post(post_id)

        return render_template('edit_post.html', post=post), 200

    if request.method == 'POST':
        print('edit_post ', post_id)
        p = Post()
        p = p.get_and_set_post(post_id)

        # get the values
        title = request.form['title']
        content = request.form['content']

        print('\n', content)

        # make the psot
        # p = Post(title=title, content=content)
        if title:
            p.title = title

        if content:
            p.content = content

        p.update_post(post_id)

        if p.get_post(p.post_id):
            # if you have a status code here it doesn't redirect
            return redirect(url_for('posts.get_posts'))
        else:
            return 'Oh no something went wrong :(', 404


@post_blueprint.route('/delete/<int:post_id>', methods=['GET', 'POST'])
def delete_post(post_id):
    p = Post()
    p.remove_post(post_id)
    return redirect(url_for('posts.get_posts'))
