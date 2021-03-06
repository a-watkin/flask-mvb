import os
import sys
import datetime

from flask import Blueprint, jsonify, request, render_template, redirect, url_for
# for markdown
import mistune


try:
    from .blog.post import Post
    from .tag.tag import Tag
    from .common.utils import login_required
except Exception as e:
    print('post routes import error', print(sys.path))
    print('\n', os.getcwd(), '\n')
    from blog.post import Post
    from common.utils import login_required
    from tag.tag import Tag

blog_blueprint = Blueprint('blog', __name__)


@blog_blueprint.route('/', methods=['GET'])
def get_posts():
    p = Post()
    posts = p.get_posts()
    markdown = mistune.Markdown()
    for post in posts:
        post['content'] = markdown(post['content'])
    return render_template('blog/posts.html', posts=posts), 200


@blog_blueprint.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    p = Post()
    post = p.get_post(post_id)
    if post:
        markdown = mistune.Markdown()
        post[0]['content'] = markdown(post[0]['content'])
    return render_template('blog/post.html', post=post), 200


@blog_blueprint.route('/new/', methods=['GET', 'POST'])
@login_required
def create_post():
    print('hello from create post ')
    if request.method == 'GET':
        return render_template('blog/new_post.html'), 200
    if request.method == 'POST':
        # get the values
        title = request.form['title']
        content = request.form['content']

        # Tag data
        tags = request.form['tags']
        tags_data = tags.split(',')

        p = Post(title=title, content=content)

        if 'publish' in request.form:
            publish = datetime.datetime.now()
            p.datetime_published = publish

        p.create_post()

        # Add tags to the post
        t = Tag()
        t.add_tags_to_post(p.post_id, tags_data)

        if p.get_post(p.post_id):
            # if you have a status code here it doesn't redirect
            return redirect(url_for('blog.get_posts'))
        else:
            return 'Oh no something went wrong :(', 404


@blog_blueprint.route('/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    if request.method == 'GET':
        p = Post()
        post = p.get_post(post_id)

        return render_template('blog/edit_post.html', post=post), 200

    if request.method == 'POST':
        print('edit_post ', post_id)
        p = Post()
        p = p.get_and_set_post(post_id)

        # get the values
        title = request.form['title']
        content = request.form['content']

        # Tag data
        tags = request.form['tags']
        tags_data = tags.split(',')

        if 'publish' in request.form:
            publish = datetime.datetime.now()
            p.datetime_published = publish
        else:
            publish = None
            p.datetime_published = publish

        p.title = title
        p.content = content

        p.update_post(post_id)

        # Add tags to the post
        t = Tag()
        t.add_tags_to_post(p.post_id, tags_data)

        if p.get_post(p.post_id):
            # if you have a status code here it doesn't redirect
            return redirect(url_for('blog.edit_post', post_id=p.post_id))
        else:
            return 'Oh no something went wrong :(', 404


@blog_blueprint.route('/delete/<int:post_id>', methods=['GET', 'POST'])
@login_required
def delete_post(post_id):
    p = Post()
    p.remove_post(post_id)
    return redirect(url_for('blog.get_posts'))


@blog_blueprint.route('/deleted', methods=['GET', 'POST'])
@login_required
def deleted_posts():
    p = Post()
    deleted_posts = p.get_deleted_posts()
    return render_template('blog/deleted_posts.html', posts=deleted_posts)


@blog_blueprint.route('/restore/<int:post_id>', methods=['GET'])
@login_required
def restore_post(post_id):
    print('\n\nwhat is the request', request.method, '\n\n')
    p = Post()
    p.restore_post(post_id)
    return redirect(url_for('blog.deleted_posts'))


@blog_blueprint.route('/purge', methods=['GET'])
@login_required
def purge_deleted_posts():
    p = Post()
    p.purge_deleted_posts()
    return redirect(url_for('blog.get_posts'))


@blog_blueprint.route('/delete/all', methods=['GET'])
@login_required
def delete_all_posts():
    p = Post()
    p.delete_all_posts()
    return redirect(url_for('blog.get_posts'))
