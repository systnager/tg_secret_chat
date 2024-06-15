import sqlite3


class Database:
    def __init__(self):
        self.connection = sqlite3.connect('database.db')

    def start_connection(self) -> None:
        self.connection = sqlite3.connect('database.db')

    def close_connection(self) -> None:
        self.connection.close()

    def complete_sql_request(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()
        return cursor.fetchall()

    def write_new_item(self, table: str, columns_params: dict):
        columns_clause = ', '.join([f"{col}" if isinstance(col, str) else str(col) for col in columns_params.keys()])
        values_clause = ', '.join([f"'{val}'" if isinstance(val, str) else str(val) for val in columns_params.values()])
        request = f'INSERT INTO {table} ({columns_clause}) VALUES ({values_clause});'
        self.complete_sql_request(request)

    def get_item(self, table, columns='*', filter_params=None):
        if filter_params is None:
            filter_params = {}

        where_clause = " AND ".join(f"{col} = '{val}'" if isinstance(val, str) else f"{col} = {val}"
                                    for col, val in zip(filter_params.keys(), filter_params.values())) if not (filter_params is None) else ''
        set_clause = "*" if columns == '*' else ", ".join(columns)
        where_clause = " WHERE " + where_clause if where_clause else ""
        request = f"SELECT {set_clause} FROM {table} {where_clause};"
        return self.complete_sql_request(request)

    def update_item(self, table, columns_params=None, filter_params=None):
        if columns_params is None:
            columns_params = {}
        if filter_params is None:
            filter_params = {}

        set_clause = ", ".join(f"{col} = '{val}'" if isinstance(val, str) else f"{col} = {val}"
                               for col, val in zip(columns_params.keys(), columns_params.values()))

        where_clause = " AND ".join(f"{col} = '{val}'" if isinstance(val, str) else f"{col} = {val}"
                                    for col, val in zip(filter_params.keys(), filter_params.values())) if not (filter_params is None) else ''

        where_clause = " WHERE " + where_clause if where_clause else ""
        request = f"UPDATE {table} SET {set_clause} {where_clause};"
        self.complete_sql_request(request)

    def get_user(self, user_id: int):
        user = self.get_item('user', '*', {'id': user_id})
        return user[0] if user else None

    def get_users_by_room_code(self, room_code):
        return self.get_item('user', '*', {'room_code': room_code})

    def get_users(self):
        return self.get_item('user', '*')

    def get_admins(self):
        return self.get_item('user', '*', {'id': 'admin'})

    def add_new_user(self, user_id, room_code='NULL', state='default'):
        user_info = {
            'id': user_id,
            'state': state,
            'role': 'user',
            'room_code': room_code,
        }

        self.write_new_item('user', user_info)

    def changer_user_state(self, user_id: int, state: str):
        self.update_item('user', {'state': state}, {'id': user_id})

    def changer_user_room_code(self, user_id: int, room_code: str):
        self.update_item('user', {'room_code': room_code}, {'id': user_id})

    def get_user_room_code(self, user_id: int):
        user = self.get_user(user_id)
        return user[3] if user else None

    def delete_user(self, user_id: int) -> None:
        query = f'DELETE FROM user WHERE id = {user_id};'
        self.complete_sql_request(query)
