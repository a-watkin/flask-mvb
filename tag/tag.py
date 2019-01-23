import os
import sys
import datetime
import urllib.parse

try:
    """
    Running as flask app.
    """
    from common.utils import get_id, name_util
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


class Tag(object):

    def __init__(self):
        self.db = Database()

    def get_count_by_tag(self, entity_id, entity_table, tag_table, tag_name):
        """
        Entity table is the table of the thing you want the count for, e.g. post, photo, project etc

        tag table is the linking table
        """
        query_string = '''
            SELECT COUNT({}) FROM {}
            JOIN {} using({})
            where tag_name = "{}"
        '''.format(
            entity_id,
            entity_table,
            tag_table,
            entity_id,
            tag_name
        )

        photo_count = self.db.get_query_as_list(query_string)

        return photo_count

    def check_forbidden(self, tag_name):
        print('hello from check_forbidden')
        print(tag_name)

        forbidden = [";", "/", "?", ":", "@", "=", "&", '"', "'", "<", ">",
                     "#", "%", "{", "}", "|", "\\", "/", "^", "~", "[", "]", "`"]
        for char in tag_name:
            if char in forbidden:
                return urllib.parse.quote(tag_name, safe='')

        return tag_name

    def decode_tag(self, tag_name):
        return urllib.parse.unquote(tag_name)

    def get_all_tag_names(self):
        """
        Get all tag names as a list.
        """
        tag_data = self.db.get_query_as_list(
            '''
            SELECT tag_name FROM tag ORDER BY tag_name
            '''
        )

        tags = []

        for tag in tag_data:
            tags.append(list(tag.values())[0])

        return tags

    def entity_tag_list(self, post_id):
        tag_data = self.db.get_query_as_list(
            '''
            SELECT tag_name FROM post_tag 
            WHERE post_id = {}
            ORDER BY tag_name
            '''.format(post_id)
        )

        tags = []

        for tag in tag_data:
            tags.append(list(tag.values())[0])

        return tags

    def get_entity_tags(self, entity_name, entity_id):

        if entity_name == 'post':
            print('entity name post')
            query_string = '''
                select post_tag.tag_name from post
                join post_tag on(post_tag.post_id=post.post_id)
                where post.post_id={}
            '''.format(entity_id)

        if entity_name == 'photo':
            query_string = '''
                select photo_tag.tag_name from photo
                join photo_tag on(photo_tag.photo_id=photo.photo_id)
                where photo.photo_id={}
            '''.format(entity_id)

        print('query_string\n', query_string)

        # so an array of tags would be ok
        tag_data = self.db.get_query_as_list(query_string)
        for tag in tag_data:
            # print(self.decode_tag(tag['tag_name']))

            tag['human_readable_tag'] = self.decode_tag(tag['tag_name'])

        # print(tag_data)

        return tag_data

    def get_tag(self, tag_name):
        """
        Changed to return human_readable_tag

        Might cause problems because before it was pointlesly returning none.
        """
        tag_data = self.db.make_query(
            '''
            select tag_name from tag where tag_name = "{}"
            '''.format(tag_name)
        )

        if len(tag_data) > 0:
            tag_name = tag_data[0][0]
            human_readable_tag = name_util.make_decoded(tag_data[0][0])

            rtn_dict = {
                'tag_name': tag_name,
                'human_readable_name': human_readable_tag
            }

            return rtn_dict

    def check_tag(self, tag_name):
        """
        Check that a tag has been added.
        """
        data = self.db.make_query(
            '''select * from photo_tag where tag_name = "{}" '''
            .format(tag_name))

        if len(data) > 0:
            return True
        return False

    def remove_tag_name(self, tag_name):
        if '%' in tag_name:
            tag_name = urllib.parse.quote(tag_name, safe='')

        # tag_name = name_util.url_encode_tag(tag_name)

        self.db.make_query(
            '''
            delete from tag where tag_name = "{}"
            '''.format(tag_name)
        )

        self.db.make_query(
            '''
            delete from photo_tag where tag_name = "{}"
            '''.format(tag_name)
        )

        self.update_photo_count(tag_name)

    def delete_tag(self, tag_name):
        # you have to remove the tag from the tag table
        self.db.delete_rows_where('tag', 'tag_name', tag_name)
        # and also in photo_tag
        self.db.delete_rows_where('photo_tag', 'tag_name', tag_name)

        if not self.get_tag(tag_name) and not self.check_photo_tag(tag_name):
            return True
        else:
            return False

    def replace_tags(self, photo_id, tag_list):
        """
        Replaes the tags attached to a photo with new tags.
        """
        # get all the tags attached to the photo
        current_tags = self.db.make_query(
            '''
            select * from photo_tag where photo_id = {}
            '''.format(photo_id)
        )

        print(current_tags)

        # remove the current tags
        self.db.make_query(
            '''
            delete from photo_tag where photo_id = {}
            '''.format(photo_id)
        )

        for tag in tag_list:
            # add tags in the tag_list
            self.db.make_query(
                '''
                insert into photo_tag (photo_id, tag_name)
                values ({}, "{}")
                '''.format(photo_id, tag)
            )

            self.update_photo_count(tag)

    def add_tags_to_photo(self, photo_id, tag_list):
        """
        Adds tags to a photo.

        First checking if the tag is already in the tag table, if not it adds it.

        Then it adds the tag to photo_tag which links the photo and tag tables.
        """
        print('\nHello from add_tags_to_photo, the tag list is: ', tag_list)

        # for each tag
        # check if the tag is in the database already
        # if it is not then add it to the tag table
        for tag in tag_list:

            # will return None if the tag is not in the tag table
            # tag_name is the column name
            data = self.db.get_row('tag', 'tag_name', tag)

            print('data is', data)

            if data is None:

                print('\nthat value {} is not in the db\n'.format(tag))

                self.db.make_query(
                    '''
                    insert into tag (tag_name, username, photos)
                    values ("{}", "{}", {})
                    '''.format(
                        tag,
                        '28035310@N00',
                        self.get_photo_count_by_tag(tag)
                    )
                )

                print('\nshould be added now...\n')

                if self.db.get_row('tag', 'tag_name', tag):
                    print('\nadded tag, ', tag, '\n')

            # UNIQUE constraint can cause problems here
            # so catch any exceptions
            try:
                # The tag is now in the database.
                self.db.make_query(
                    '''
                    insert into photo_tag (photo_id, tag_name)
                    values ({}, "{}")
                    '''.format(photo_id, tag)
                )
            except Exception as e:
                print('Problem adding tag to photo_tag ', e)

        data = self.db.make_query(
            '''
            select * from photo_tag where photo_id = {}
            '''.format(photo_id)
        )

        tags_in_data = []
        if len(data) > 0:
            for tag in data:
                tags_in_data.append(tag[1])

        print(tags_in_data)
        for tag in tag_list:
            if tag not in tags_in_data:
                return False
            else:
                self.update_photo_count(tag)

        return True

    def update_tag(self, new_tag, old_tag):
        print('hello from update_tag - passed values, ', new_tag, old_tag)
        # check if new tag exists
        test = self.db.make_query(
            '''
            select * from tag where tag_name = "{}"
            '''.format(new_tag)
        )

        # print(test)

        if not test:
            # if the tag doesn't exist already then update it
            # existing tag to the new tag
            self.db.make_query(
                '''
                update tag
                set tag_name = "{}"
                where tag_name = "{}"
                '''.format(new_tag, old_tag)
            )

        # if new tag exists or not you have to update photo_tag
        self.db.make_query(
            '''
            update photo_tag
            set tag_name = "{}"
            where tag_name = "{}"
            '''.format(new_tag, old_tag)
        )

        # update the photo count for the tag table
        self.update_photo_count(new_tag)

        if self.get_tag(new_tag) and not self.get_tag(old_tag):
            return True
        else:
            return False

    def get_entity_by_tag(self, entity, tag_name):
        """
        Get all the photos that are associated with a particular tag.

        I will need to handle spaces.
        """
        # q_data = None

        if entity == 'photo':
            query_string = '''
                select photo_id, photo_title, views, tag_name, large_square from photo
                join photo_tag using(photo_id)
                join images using(photo_id)
                where tag_name = "{}"
                order by views desc
            '''.format(tag_name)

        if entity == 'post':
            query_string = '''
                SELECT post_id, title, content, datetime_posted, datetime_published FROM post
                JOIN post_tag USING(post_id)
                WHERE tag_name = "{}"
                ORDER BY datetime_posted DESC
            '''.format(tag_name)

        tag_data = self.db.get_query_as_list(query_string)

        for data in tag_data:
            data['tags'] = self.get_entity_tags(
                entity, data['{}_id'.format(entity)])

        return tag_data

    def remove_post_tags(self, post_id):
        self.db.make_query(
            '''
            DELETE FROM post_tag WHERE post_id = {}
            '''.format(post_id)
        )

    def add_tags_to_post(self, post_id, tags):
        current_tags = self.get_all_tag_names()
        # list of tags already assocaited with a post
        post_tags = self.entity_tag_list(post_id)

        # delete all current tags belonging to the post
        if len(post_tags) > 0:
            self.remove_post_tags(post_id)

            # If the tag is not in the tag table
        for tag in tags:
            tag = tag.strip()
            if tag not in current_tags:
                print('inserting tag ', tag)
                self.insert_tag(tag)
                self.add_to_post_tag(post_id, tag)

            # If the tag is in the tag table
            elif tag in current_tags:
                self.add_to_post_tag(post_id, tag)

    def insert_tag(self, tag):
        self.db.make_query(
            '''
        insert into tag (tag_name, username, posts)
        values ("{}", "{}", {})
        '''.format(
                tag,
                'a',
                1
            )
        )

    def add_to_post_tag(self, post_id, tag_name):
        print('add_to_post_tag', post_id, tag_name)
        query_string = '''
            INSERT INTO post_tag (post_id, tag_name)
            VALUES (?, ?)
            '''

        data = (
            post_id,
            tag_name
        )

        print('data values are ', data)

        if self.db.make_sanitized_query(query_string, data):
            return True
        return False

    # def data_for_edit_tag(self):


if __name__ == "__main__":
    t = Tag()

    # print(t.get_all_tag_names())

    # print(t.get_entity_tags('post', 2789896248))

    # print(t.entity_tag_list(2789896248))

    # t.remove_post_tags(2789896248)

    # t.add_tags_to_post(1431516958, ['apples', 'oranges'])

    # t.add_tags_to_post(2754678461, 'test')

    print(t.get_entity_by_tag('post', 'tag'))
