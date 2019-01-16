

try:
    from .blog_db import Database

    from .password_util import PasswordUtil
except Exception as e:
    from blog_db import Database

    from password_util import PasswordUtil


class User(object):
    def __init__(self, username, password=None, _id=None):
        self.username = username
        self.password = password
        self.user_id = None
        # init database
        self.db = Database()

    # check if username exists
    def check_for_username(self):
        """
        Checks if the username is in the database.
        """
        db_resp = self.db.get_row('user', 'username', self.username)
        if db_resp is None:
            return False
        return True

    def get_hashed_password(self, username):
        """
        Returns the hasehd password from the database for the given username.
        """
        db_resp = self.db.get_row('user', 'username', self.username)

        # print(db_resp)
        if db_resp:
            return db_resp[0]['hash']
        # changed here because the db no longer returns a tuple
        # return db_resp[2]

    def insert_hased_password(self, password):
        """
        Inserts hashed password into the database.

        Replaces password if already there.
        """
        # get hashed version
        hased_password = PasswordUtil.hash_password(password)
        self.db.make_query(
            '''
            UPDATE user 
            SET hash = "{}"
            WHERE username = "{}"
            '''.format(hased_password, self.username)
        )
        # print(hased_password)

    def check_password(self):
        hashed_password = self.get_hashed_password(self.username)
        return PasswordUtil.check_hashed_password(self.password, hashed_password)


def main():
    u = User('a', 'a')
    # hased password has been inserted
    print(u.get_hashed_password('a'))

    print(u.check_password())


if __name__ == '__main__':
    main()
