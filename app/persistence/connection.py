from mysql.connector import pooling
from mysql.connector.pooling import MySQLConnectionPool
from typing import Self, Any, TypedDict, cast
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

class PoolConfig(TypedDict, total=False):
    pool_name: str
    pool_size: int
    host: str
    database: str
    user: str
    password: str
    port:int
    

class MySQLConnectionPoolBuilder:
    def __init__(self, params: PoolConfig | None = None):
        default_config: PoolConfig = {
            'pool_name': 'my_pool',
            'pool_size': 5,
            'host': 'localhost',
            'database': 'db',
            'user': 'user',
            'password': 'user1234',
            'port': 3306
        }
        params = params or {}
        self._pool_config: PoolConfig = {**default_config, **params}


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

def create_tables(connection_pool: MySQLConnectionPool) -> None:
    with connection_pool.get_connection() as conn:
        cursor = conn.cursor()

        teams_table_sql = '''
                create table if not exists teams (
                    id_ integer primary key auto_increment,
                    name varchar(50) not null,
                    points integer default 0
                );
            '''

        players_table_sql = '''
                create table if not exists players (
                    id_ integer primary key auto_increment,
                    name varchar(50) not null,
                    goals integer default 0,
                    team_id integer,
                    foreign key (team_id) references teams(id_) on delete cascade on update cascade
                );
            '''
        cursor.execute(teams_table_sql)
        cursor.execute(players_table_sql)

def drop_tables(connection_pool: MySQLConnectionPool) -> None:
    with connection_pool.get_connection() as conn:
        cursor = conn.cursor()

        drop_players_table_sql = "drop table if exists players;"
        drop_teams_table_sql = "drop table if exists teams;"
        cursor.execute(drop_players_table_sql)
        cursor.execute(drop_teams_table_sql)