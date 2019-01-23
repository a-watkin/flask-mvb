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

tag_blueprint = Blueprint('tag', __name__)


@tag_blueprint.route('/', methods=['GET'])
def get_all_tags():
    t = Tag()
    tags = t.get_all_tags()

    print(tags)

    return render_template('tag/tags.html', tags=tags), 200


@tag_blueprint.route('/<string:tag_name>', methods=['GET'])
def get_posts_by_tag(tag_name):
    t = Tag()
    posts = t.get_entity_by_tag('post', tag_name)

    print(posts)

    return render_template('blog/posts.html', posts=posts), 200
