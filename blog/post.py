import os
import sys
import datetime

try:
    """
    Running as flask app.
    """
    from common.utils import get_id
    from common.db_interface import Database
except Exception as e:
    """
    Running as module.
    """
    print('\npost running as a module, for testing\n')
    print('post.py import problem ', e)
    # adding the root directory of the projects
    sys.path.append('/home/a/projects/flask-mvb')
    print('added to path ', sys.path)
    from common.utils import get_id
    from common.db_interface import Database


class Post(object):
    def __init__(self, *args, **kwargs):
        # print(args, '\nkwargs\n', kwargs)

        for dictionary in args:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            # print('key', key)
            setattr(self, key, kwargs[key])
        # access to the db
        self.db = Database()

        # really not ideal but i need some deault values beyond just None for a lot of these
        if 'post_id' not in self.__dict__:
            # print('No post_id, so adding it')
            self.post_id = get_id()

        if 'username' not in self.__dict__:
            # print('No username, so adding it')
            self.username = 'a'

        if 'title' not in self.__dict__:
            # print('No title, so adding it')
            self.title = None

        if 'content' not in self.__dict__:
            # print('No content, so adding it')
            self.content = None

        if 'datetime_posted' not in self.__dict__:
            # print('No datetime_posted, so adding it')
            self.datetime_posted = datetime.datetime.now()

        if 'datetime_published' not in self.__dict__:
            # print('No datetime_published, so adding it')
            self.datetime_published = None

    def __repr__(self):
        pass

    def __str__(self):
        return '''
        A blog post: \n
        post_id: {}\n
        username: {}\n
        title: {}\n
        content: {}\n
        datetime_posted: {}\n
        datetime_published: {}\n
        '''.format(
            self.post_id,
            self.username,
            self.title,
            self.content,
            self.datetime_posted,
            self.datetime_published
        )

    def get_posts(self):
        data = self.db.get_query_as_list(
            '''
            SELECT * FROM post ORDER BY datetime_posted DESC
            '''
        )

        return data

    def get_deleted_posts(self):
        data = self.db.get_query_as_list(
            '''
            SELECT * FROM deleted_post ORDER BY datetime_posted DESC
            '''
        )

        # data = self.db.get_rows('post')
        return data

    def get_deleted_post(self, post_id):
        data = self.db.get_query_as_list(
            '''
            SELECT * FROM deleted_post WHERE post_id = {}
            '''.format(post_id)
        )

        # data = self.db.get_rows('post')
        return data

    def purge_deleted_posts(self):
        self.db.make_query(
            '''
            DELETE FROM deleted_post
            '''
        )

        if self.get_deleted_posts():
            return False
        return True

    def get_post(self, post_id):
        data = self.db.get_row('post', 'post_id', post_id)
        return data

    def get_and_set_post(self, post_id):
        data = self.get_post(post_id)
        if data:
            return Post(data[0])

    def create_post(self):
        query_string = '''
            INSERT INTO post (post_id, username, title, content, datetime_posted, datetime_published)
            VALUES (?, ?, ?, ?, ?, ?)
            '''

        data = (
            self.post_id,
            self.username,
            self.title,
            self.content,
            self.datetime_posted,
            self.datetime_published,
        )

        self.db.make_sanitized_query(query_string, data)

    def update_post(self, post_id):
        """
        post_id shouldn't change.
        """
        if self.get_post(post_id):
            query_string = '''
                UPDATE post
                SET title = ?, content = ?, datetime_posted = ?, datetime_published = ?
                WHERE post_id = ?
                '''

            data = (
                self.title,
                self.content,
                self.datetime_posted,
                self.datetime_published,
                self.post_id
            )

            self.db.make_sanitized_query(query_string, data)

            return True
        else:
            return False

    def save_deleted_post(self):
        query_string = '''
            INSERT INTO deleted_post (post_id, username, title, content, datetime_posted, datetime_published)
            VALUES (?, ?, ?, ?, ?, ?)
            '''

        data = (
            self.post_id,
            self.username,
            self.title,
            self.content,
            self.datetime_posted,
            self.datetime_published,
        )

        self.db.make_sanitized_query(query_string, data)

    def remove_post(self, post_id):
        post_data = self.get_post(post_id)

        if post_data:
            p = Post(post_data[0])
            p.save_deleted_post()

            self.db.make_query(
                '''
                DELETE FROM post WHERE post_id = "{}";
                '''.format(post_id)
            )

            if self.get_post(post_id):
                return True

        return False

    def restore_post(self, post_id):
        # gets the post data
        post = self.get_deleted_post(post_id)
        # make a new Post object
        if post:
            post = post[0]
            # New instance of Post using the data from the deleted_post
            post_to_restore = Post(post)
            # write the post to the post table
            post_to_restore.create_post()
            # remove the post from deleted post table
            post_to_restore.remove_deleted_post(post_id)

    def remove_deleted_post(self, post_id):
        """
        Remove a post from deleted_post table and check that it is gone.
        """
        self.db.make_query(
            '''
            DELETE FROM deleted_post WHERE post_id = "{}";
            '''.format(post_id)
        )

        if self.get_deleted_post(post_id):
            return False

        return True

    def delete_all_posts(self):
        """
        Not implimented at the frontend.
        """
        self.db.make_query(
            '''
            DELETE FROM post
            '''
        )


if __name__ == "__main__":
    p = Post()

    print(p.get_post(6558864814))
