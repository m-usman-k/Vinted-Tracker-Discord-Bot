from sqlite3 import connect, Error

class User:
    def __init__(self, id: int, name: str, filter_name: str, filter_link: str):
        self.id = id
        self.name = name
        self.filter_name = filter_name
        self.filter_link = filter_link

class Database:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.check_n_create_tables()

    def connect(self):
        try:
            connection = connect(self.db_name)
            return connection
        except Error as e:
            print(f"Connection error: {e}")
            return None

    def check_n_create_tables(self):
        # Ensure proper closure of connection using context manager
        with self.connect() as connection:
            if connection is None:
                return

            cursor = connection.cursor()

            create_table_query = """
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY NOT NULL,
                name TEXT NOT NULL,
                filter_name TEXT,
                filter_link TEXT
            );
            """

            try:
                cursor.execute(create_table_query)
                print("Table 'user' checked/created successfully.")
            except Exception as e:
                print(f"An error occurred: {e}")

    def check_n_get_user(self, id, name) -> User:
        with self.connect() as connection:
            if connection is None:
                return

            cursor = connection.cursor()

            get_user_query = """
            SELECT * FROM user WHERE id = ? AND name = ?;
            """

            try:
                cursor.execute(get_user_query, (id, name))
                user = cursor.fetchone()

                if user:
                    return User(id=user[0], name=user[1], filter_name=user[2], filter_link=user[3])
                else:
                    print(f"User with ID {id} and name {name} not found.")
                    return None
            except Exception as e:
                print(f"An error occurred: {e}")
                return None

    def get_all_users(self) -> list[User]:
        with self.connect() as connection:
            if connection is None:
                return []

            cursor = connection.cursor()

            get_user_query = """
            SELECT * FROM user;
            """

            try:
                cursor.execute(get_user_query)
                all_users = cursor.fetchall()
                list_of_users = [User(id=user[0], name=user[1], filter_name=user[2], filter_link=user[3]) for user in all_users]
                return list_of_users
            except Exception as e:
                print(f"An error occurred: {e}")
                return []

    def update_user(self, user: User) -> User:
        with self.connect() as connection:
            if connection is None:
                return None

            cursor = connection.cursor()

            upsert_query = """
            INSERT INTO user (id, name, filter_name, filter_link)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET 
                name = excluded.name,
                filter_name = excluded.filter_name,
                filter_link = excluded.filter_link;
            """

            try:
                cursor.execute(upsert_query, (user.id, user.name, user.filter_name, user.filter_link))

                select_query = "SELECT * FROM user WHERE id = ?;"
                result = cursor.execute(select_query, (user.id,)).fetchone()

                if result:
                    return User(*result)
                else:
                    print(f"User with ID {user.id} could not be retrieved after UPSERT.")
                    return None
            except Exception as e:
                print(f"An error occurred: {e}")
                return None
