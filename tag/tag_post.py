import urllib.parse
import sqlite3


from database_interface import Database
import name_util


class Tag(object):

    def __init__(self):
        self.db = Database('eigi-data.db')

    def get_post_count_by_tag(self, tag_name):
        query_string = '''
            select count(post_id) from post
            join post_tag using(post_id)
            where tag_name = "{}"
        '''.format(tag_name)

        post_count = self.db.get_query_as_list(query_string)

        if len(post_count) > 0:
            return post_count[0]['count(post_id)']

    def update_post_count(self, tag_name):
        """
        Updates the post count for the given tag.
        """
        count = self.get_post_count_by_tag(tag_name)

        self.db.make_query(
            '''
            update tag
            set posts = {}
            where tag_name = "{}"
            '''.format(count, tag_name)
        )

    def check_all_tag_post_counts(self):
        """
        Gets a count of all the posts associated with a tag.
        Checks that the posts column in tag is up to date.
        """
        data = self.db.get_query_as_list(
            '''
            select * from tag
            '''
        )

        for tag in data:
            print()
            print(tag)
            # query for the number of posts using the tag
            # compare it to the number in the posts column
            # update if necessary
            query_count = self.db.get_query_as_list(
                '''
                select count(tag_name)
                from post_tag
                where tag_name = "{}"
                '''.format(tag['tag_name'])
            )

            if query_count[0]['count(tag_name)'] == tag['posts']:
                print('OK', 'actual posts number with tag',
                      query_count[0]['count(tag_name)'], 'in posts column', tag['posts'])
            else:
                print('MISSMATCH IN postS AND postS WITH TAG\n', 'actual posts number with tag',
                      query_count[0]['count(tag_name)'], 'in posts column', tag['posts'])

                tag_name = tag['tag_name']
                count = query_count[0]['count(tag_name)']
                break

        print('\nDONE NO PROBLEMS!')

    def remove_zero_post_tags(self):
        self.check_all_tag_post_counts()

        zero_posts = self.db.make_query(
            '''
            delete from tag where posts = 0
            '''
        )

    def get_zero_post_tag_count(self):
        return self.db.make_query(
            '''
            select count(posts) from tag where posts = 0
            '''
        )[0][0]

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

    def get_all_tags(self):
        # as a list of dict values
        tag_data = self.db.get_query_as_list(
            "SELECT tag_name, posts FROM tag order by tag_name"
        )

        rtn_dict = {

        }

        count = 0
        for tag in tag_data:
            rtn_dict[count] = tag
            tag_name = tag['tag_name']
            # adding the number of posts with the tag
            rtn_dict[count]['posts'] = tag['posts']
            rtn_dict[count]['human_readable_tag'] = self.decode_tag(
                tag['tag_name'])
            count += 1

        return rtn_dict

    def get_post_tags(self, post_id):
        """
        Get the tags for a single post.

            select post.post_id, post.post_title, post_tag.tag_name from post
            join post_tag on(post_tag.post_id=post.post_id)
            where post.post_id={}

        """

        query_string = '''
            select post_tag.tag_name from post
            join post_tag on(post_tag.post_id=post.post_id)
            where post.post_id={}
        '''.format(post_id)

        # so an array of tags would be ok
        tag_data = self.db.get_query_as_list(query_string)
        for tag in tag_data:
            # print(self.decode_tag(tag['tag_name']))

            tag['human_readable_tag'] = self.decode_tag(tag['tag_name'])

        # print(tag_data)

        return tag_data

    def get_posts_by_tag(self, tag_name):
        """
        Get all the posts that are associated with a particular tag.

        I will need to handle spaces.
        """
        # q_data = None

        query_string = '''
            select post_id, post_title, views, tag_name, large_square from post
            join post_tag using(post_id)
            join images using(post_id)
            where tag_name = "{}"
            order by views desc
        '''.format(tag_name)

        tag_data = self.db.get_query_as_list(query_string)

        # print(tag_data)

        rtn_dict = {
            'tag_info': {'number_of_posts': self.get_post_count_by_tag(tag_name)}
        }

        count = 0
        for t in tag_data:
            rtn_dict[count] = t
            rtn_dict[count]['human_readable_tag'] = name_util.make_decoded(
                rtn_dict[count]['tag_name'])
            count += 1

        return rtn_dict

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

    def check_post_tag(self, tag_name):
        """
        Check that a tag has been added.
        """
        data = self.db.make_query(
            '''select * from post_tag where tag_name = "{}" '''
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
            delete from post_tag where tag_name = "{}"
            '''.format(tag_name)
        )

        self.update_post_count(tag_name)

    def delete_tag(self, tag_name):
        # you have to remove the tag from the tag table
        self.db.delete_rows_where('tag', 'tag_name', tag_name)
        # and also in post_tag
        self.db.delete_rows_where('post_tag', 'tag_name', tag_name)

        if not self.get_tag(tag_name) and not self.check_post_tag(tag_name):
            return True
        else:
            return False

    def clean_tags(self):
        forbidden = ['.', ';', '%']
        # as a list of dict values
        tag_data = self.db.get_query_as_list("SELECT * FROM tag")
        for tag in tag_data:
            print(tag['tag_name'], tag['tag_name'] in forbidden)
            if tag['tag_name'] in forbidden:
                print('please just ket me die already, ', tag['tag_name'])
                self.remove_tag_name(tag['tag_name'])

        tag_data = self.db.get_query_as_list("SELECT * FROM post_tag")
        for tag in tag_data:
            print(tag['tag_name'], tag['tag_name'] in forbidden)
            if tag['tag_name'] in forbidden:
                print('please just ket me die already, ', tag['tag_name'])
                self.remove_tag_name(tag['tag_name'])

    def remove_tags_from_post(self, post_id, tag_list):
        for tag in tag_list:
            print(tag)

            # if the tag isn't present it will just fail silently
            resp = self.db.make_query(
                '''
                delete from post_tag
                where post_id = {}
                and tag_name = "{}"
                '''.format(post_id, tag)
            )
            print(resp)

            self.update_post_count(tag)

    def replace_tags(self, post_id, tag_list):
        """
        Replaes the tags attached to a post with new tags.
        """
        # get all the tags attached to the post
        current_tags = self.db.make_query(
            '''
            select * from post_tag where post_id = {}
            '''.format(post_id)
        )

        print(current_tags)

        # remove the current tags
        self.db.make_query(
            '''
            delete from post_tag where post_id = {}
            '''.format(post_id)
        )

        for tag in tag_list:
            # add tags in the tag_list
            self.db.make_query(
                '''
                insert into post_tag (post_id, tag_name)
                values ({}, "{}")
                '''.format(post_id, tag)
            )

            self.update_post_count(tag)

    def add_tags_to_post(self, post_id, tag_list):
        """
        Adds tags to a post.

        First checking if the tag is already in the tag table, if not it adds it.

        Then it adds the tag to post_tag which links the post and tag tables.
        """
        print('\nHello from add_tags_to_post, the tag list is: ', tag_list)

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
                    insert into tag (tag_name, user_id, posts)
                    values ("{}", "{}", {})
                    '''.format(
                        tag,
                        '28035310@N00',
                        self.get_post_count_by_tag(tag)
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
                    insert into post_tag (post_id, tag_name)
                    values ({}, "{}")
                    '''.format(post_id, tag)
                )
            except Exception as e:
                print('Problem adding tag to post_tag ', e)

        data = self.db.make_query(
            '''
            select * from post_tag where post_id = {}
            '''.format(post_id)
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
                self.update_post_count(tag)

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

        # if new tag exists or not you have to update post_tag
        self.db.make_query(
            '''
            update post_tag
            set tag_name = "{}"
            where tag_name = "{}"
            '''.format(new_tag, old_tag)
        )

        # update the post count for the tag table
        self.update_post_count(new_tag)

        if self.get_tag(new_tag) and not self.get_tag(old_tag):
            return True
        else:
            return False

    def count_posts_by_tag_name(self, tag_name):
        """

        """
        print('count_posts_by_tag_name, passed ', tag_name)

        count = self.db.make_query(
            '''
            select count(tag_name)
            from post_tag
            where tag_name = "{}"
            '''.format(tag_name)
        )

        if len(count) > 0:
            return count[0][0]
        else:
            return 0

    def get_tag_posts_in_range(self, tag_name, limit=20, offset=0):
        print('hello from get_tag_posts_in_range passed the tag ', tag_name)

        # I think flask is passing decoded values in.
        tag_name = name_util.make_encoded(tag_name)

        # get number of posts in database total
        num_posts = self.count_posts_by_tag_name(tag_name)

        print(num_posts)

        if offset > num_posts:
            offset = num_posts - (num_posts % 20)

        page = offset // limit

        pages = num_posts // limit

        # otherwise it starts at 0 and I want it to start at 1
        if num_posts == 20:
            page = 1
            pages = 1

        elif num_posts > 20 and num_posts % 20 == 0:
            page += 1

        else:
            page += 1
            pages += 1

        # guards against page being grater than pages
        if page > pages:
            print('STAHP!', offset, num_posts)
            # prevents an empty set being returned
            offset = offset - 20
            page = pages

        q_data = None
        with sqlite3.connect(self.db.db_name) as connection:
            c = connection.cursor()

            c.row_factory = sqlite3.Row

            query_string = (
                '''
                select post_id, post_title, views, tag_name, large_square from post
                join post_tag using(post_id)
                join images using(post_id)
                where tag_name = "{}"
                order by views
                desc limit {} offset {}
                '''
            ).format(tag_name, limit, offset)

            q_data = c.execute(query_string)

        rtn_dict = {
            'limit': limit,
            'offset': offset,
            'posts': []
        }

        """
        I think it may actually be better to layout what fields you want here.

        And maybe include all sizes.
        """

        data = [dict(ix) for ix in q_data]

        # Do I really need to decode the title?
        for post in data:
            if post['post_title'] is not None:
                post['post_title'] = name_util.make_decoded(
                    post['post_title'])

        a_dict = {}
        count = 0
        for d in data:
            a_dict[count] = d
            count += 1

        rtn_dict = {'posts': a_dict}

        print('\n why?')
        # not making it this far
        print('should be passing tag_name the value of ',
              tag_name, name_util.make_decoded(tag_name))

        rtn_dict['limit'] = limit
        rtn_dict['offset'] = offset
        rtn_dict['tag_name'] = tag_name
        rtn_dict['human_readable_name'] = name_util.make_decoded(tag_name)
        rtn_dict['page'] = page
        rtn_dict['pages'] = pages

        rtn_dict['tag_info'] = {
            'number_of_posts': self.get_post_count_by_tag(tag_name)
        }

        return rtn_dict


if __name__ == "__main__":
    t = Tag()
