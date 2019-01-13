import os
import sys
import datetime

try:
    """
    Running as flask app.
    """
    from .blog_db import Database
    from .utils import get_id
except Exception as e:
    """
    Running as module.
    """
    print('\nRunning as a module, for testing\n')
    # print(e)
    # sys.path.append('/home/a/flask-blog-api/app')
    # print('added to path ', sys.path)

    from utils import get_id
    from blog_db import Database


class Post(object):
    def __init__(self, *args, **kwargs):
        print(args, '\nkwargs\n', kwargs)

        for dictionary in args:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            print('key', key)
            setattr(self, key, kwargs[key])
        # access to the db
        self.db = Database()

        # really not ideal but i need some deault values beyond just None for a lot of these
        if 'post_id' not in self.__dict__:
            print('No post_id, so adding it')
            self.post_id = get_id()

        if 'username' not in self.__dict__:
            print('No username, so adding it')
            self.username = 'a'

        if 'title' not in self.__dict__:
            print('No title, so adding it')
            self.title = None

        if 'content' not in self.__dict__:
            print('No content, so adding it')
            self.content = None

        if 'datetime_posted' not in self.__dict__:
            print('No datetime_posted, so adding it')
            self.datetime_posted = datetime.datetime.now()

        if 'datetime_published' not in self.__dict__:
            print('No datetime_published, so adding it')
            self.datetime_published = None

    def __repr__(self):
        pass

    def __str__(self):
        return f'''
        A blog post: \n
        post_id: {self.post_id}\n
        title: {self.title}\n
        content: {self.content}\n
        datetime_posted: {self.datetime_posted}\n
        datetime_published: {self.datetime_published}\n
        '''

    def get_posts(self):
        data = self.db.get_rows('post')
        return data

    def get_post(self, post_id):
        print('get_post, ', post_id)
        # this query is returning an empty list
        data = self.db.get_row('post', 'post_id', post_id)
        print('get_post data, ', data)
        return data

    def create_post(self):
        print(self.db, type(self.db))
        # test says this is a tuple
        self.db.insert_data(
            table='post',
            post_id=self.post_id,
            username=self.username,
            title=self.title,
            content=self.content,
            datetime_posted=self.datetime_posted,
            datetime_published=self.datetime_published
        )

    def update_post(self, post_id):
        # these values are ok
        print('update_post, ',
              post_id,
              self.title,
              self.content,
              self.datetime_posted,
              self.datetime_published,
              self.post_id)

        """
        post_id shouldn't change.
        """

        if self.get_post(post_id):
            print('getting this far?')
            self.db.make_query(
                '''
                UPDATE post
                SET title = "{}", content = "{}", datetime_posted = "{}", datetime_published = "{}"
                WHERE post_id = {}
                '''.format(
                    self.title,
                    self.content,
                    self.datetime_posted,
                    self.datetime_published,
                    self.post_id
                )
            )

            return True
        else:
            return False

    def remove_post(self, post_id):
        self.db.make_query(
            '''
            DELETE FROM post WHERE post_id = "{}";
            '''.format(post_id)
        )

        if self.get_post(post_id):
            return False

        return True


if __name__ == "__main__":
    # p = Post(title='test')
    p = Post(
        title='hello world 2',
        content='some rambling nonsense again probably'
    )

    p.create_post()

    print(p)
