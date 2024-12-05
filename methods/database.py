from sqlite3 import connect, Error

class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name

    def connect(self):
        try:
            connection = connect(self.db_name)
            return connection
        except Error as e:
            print(f"Connection error: {e}")
            return None

    def check_n_create_tables(self):
        connection = self.connect()
        if connection is None:
            return

        create_table_query = """
        CREATE TABLE IF NOT EXISTS user (
            user_id INTEGER PRIMARY KEY,
            username TEXT NOT NULL,
            filter_link TEXT NOT NULL
        );
        """

        try:
            with connection:
                connection.execute(create_table_query)
                print("Table 'user' checked/created successfully.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def insert_user(self, username: str, filter_link: str):
        connection = self.connect()
        if connection is None:
            return

        insert_query = "INSERT INTO user (username, filter_link) VALUES (?, ?);"
        try:
            with connection:
                connection.execute(insert_query, (username, filter_link))
                print(f"User  '{username}' inserted successfully.")
        except Exception as e:
            print(f"An error occurred while inserting user: {e}")

    def get_users(self):
        connection = self.connect()
        if connection is None:
            return []

        select_query = "SELECT * FROM user;"
        try:
            with connection:
                cursor = connection.execute(select_query)
                users = cursor.fetchall()
                return users
        except Exception as e:
            print(f"An error occurred while retrieving users: {e}")
            return []

    def update_user(self, user_id: int, username: str, filter_link: str):
        connection = self.connect()
        if connection is None:
            return

        update_query = "UPDATE user SET username = ?, filter_link = ? WHERE user_id = ?;"
        try:
            with connection:
                connection.execute(update_query, (username, filter_link, user_id))
                print(f"User  with ID {user_id} updated successfully.")
        except Exception as e:
            print(f"An error occurred while updating user: {e}")

    def delete_user(self, user_id: int):
        connection = self.connect()
        if connection is None:
            return

        delete_query = "DELETE FROM user WHERE user_id = ?;"
        try:
            with connection:
                connection.execute(delete_query, (user_id,))
                print(f"User  with ID {user_id} deleted successfully.")
        except Exception as e:
            print(f"An error occurred while deleting user: {e}")