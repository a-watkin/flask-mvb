import os
import sqlite3


class Database(object):
    def __init__(self):
        self.db_name = 'minimal_viable_blog.db'

        # having some issue with importing so, specifying the path to the db
        # self.db_name = os.path.join(os.getcwd(), 'without_sql_alchemy.db')

    @classmethod
    def get_placeholders(cls, num):
        return ','.join(['?' for x in list(range(num))])

    # PROBABLY JUST NIX THIS
    # def make_db(self):
    #     try:
    #         from .db_schema import create_database
    #     except Exception as e:
    #         from db_schema import create_database
        
    #     # db_schema.create_database(name)
    #     create_database(self.db_name)
    #     if os.path.isfile(self.db_name):
    #         return True
    #     else:
    #         print('Database not created.')
    #         return False

    def delete_database(self):
        if self.db_name in os.listdir():
            try:
                os.remove(self.db_name)
                self.db_name = None
                return True
            except OSError as e:
                print('Problem: ', e)
        else:
            print('Database not found')
            return False

    # def insert_data(self, **kwargs):
    #     """
    #     This method does not work on the server.
    #     """


    #     print('\nHello from insert_data, the **kwargs values are ', kwargs,
    #           'the db name is', self.db_name)
    #     """
    #     Expects any number of named arguments but must include a table name.

    #     db.insert_data(
    #     table='tag',
    #     tag_name=new_tag,
    #     user_id='28035310@N00'
    #     )
    #     """

    #     table_name = kwargs['table']
    #     del kwargs['table']

    #     data = [tuple(kwargs.values())]

    #     print('data is ', data)

    #     placeholders = self.get_placeholders(len(kwargs))

    #     print('placeholders ', placeholders)

    #     try:
    #         with sqlite3.connect(self.db_name) as connection:
    #             c = connection.cursor()

    #             print(
    #                 'query is ',
    #                 'INSERT INTO {} VALUES({})'.format(
    #                 table_name, placeholders), data
    #             )

    #             c.executemany('INSERT INTO {} VALUES({})'.format(
    #                 table_name, placeholders), data)
    #     except Exception as e:
    #         print('insert_data problem ', e)

    def make_sanitized_query(self, query_string, data=None):
        print('make_sanitized_query')

        print(query_string)

        print(data)


        # print('make_sanitized_query query ', query_string, '\n',
        # 'data ', data
        # )
        with sqlite3.connect(os.path.join(self.db_name)) as connection:
            c = connection.cursor()
            return [x for x in c.execute(query_string, data)]

    def make_query(self, query_string):
        print(query_string)
        with sqlite3.connect(os.path.join(self.db_name)) as connection:
            c = connection.cursor()
            return [x for x in c.execute(query_string)]

    def get_row(self, table_name, id_name, id_value):
        try:
            q_data = None
            with sqlite3.connect(self.db_name) as connection:
                c = connection.cursor()
                c.row_factory = sqlite3.Row
                q_data = c.execute(
                    '''
                    SELECT * FROM {} WHERE {} = "{}"
                    '''.format(
                        table_name, id_name, id_value
                    )
                )

            return [dict(ix) for ix in q_data]

        except Exception as e:
            print('problem getting row ', e)

    def get_rows(self, table_name):
        q_data = None
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            c.row_factory = sqlite3.Row
            q_data = c.execute(
                '''
                SELECT * FROM {}
                '''.format(table_name))

        return [dict(ix) for ix in q_data]

    def get_query_as_list(self, query_string):
        q_data = None
        with sqlite3.connect(self.db_name) as connection:
            c = connection.cursor()
            c.row_factory = sqlite3.Row
            q_data = c.execute(query_string)

        return [dict(ix) for ix in q_data]


if __name__ == "__main__":
    db = Database()

