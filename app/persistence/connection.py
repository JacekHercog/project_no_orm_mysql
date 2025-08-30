from mysql.connector import pooling
from mysql.connector.pooling import MySQLConnectionPool
from typing import Self, Any
from dataclasses import field
import os
import logging

# >> pip install mysql-connector-python


# connection = pooling.MySQLConnectionPool(
#     pool_name='my_pool',
#     pool_size=5,
#     pool_reset_session=True,
#     host=os.getenv('HOST', 'localhost'),
#     database=os.getenv('DATABASE', 'db_1'),
#     user=os.getenv('USER', 'user'),
#     password=os.getenv('PASSWORD', 'user1234'),
#     port=int(os.getenv('PORT', '3307'))
# )

class MySQLConnectionPoolBuilder:
    def __init__(self, params: dict[str, Any] | None = None):
        params = {} if params is None else params
        self._pool_config: dict[str, Any] = {
            'pool_name': 'my_pool',
            'pool_size': 5,
            'host': 'localhost',
            'database': 'db_1',
            'user': 'user',
            'password': 'user1234',
            'port': 3306
        } | params

    def pool_size(self, data: int) -> Self:
        self._pool_config['pool_size'] = data
        return self

    def user(self, data: str) -> Self:
        self._pool_config['user'] = data
        return self

    def password(self, data: str) -> Self:
        self._pool_config['password'] = data
        return self

    def database(self, data: str) -> Self:
        self._pool_config['database'] = data
        return self

    def port(self, data: int) -> Self:
        self._pool_config['port'] = data
        return self

    def build(self) -> MySQLConnectionPool:
        return MySQLConnectionPool(**self._pool_config)

    @classmethod
    def builder(cls) -> Self:
        return cls()


connection_pool = MySQLConnectionPoolBuilder.builder().port(3307).build()
test_connection_pool = MySQLConnectionPoolBuilder.builder().port(3308).build()