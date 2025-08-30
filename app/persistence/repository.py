from mysql.connector import Error
from typing import Any, Self
from mysql.connector.pooling import MySQLConnectionPool
from datetime import date, datetime
import inflection
import logging
# >> pipenv install inflection

logging.basicConfig(level=logging.INFO)

class CrudRepository:

    def __init__(self, connection_pool: MySQLConnectionPool, entity: Any):
        self._connection_pool = connection_pool
        self._entity = entity
        self._entity_type = type(entity())

    # TODO Napisac wersje z try ... except oraz z context manager
    def insert(self, item: Any) -> int:
        connection = None
        cursor = None
        try:
            connection = self._connection_pool.get_connection()
            if connection.is_connected():
                cursor = connection.cursor()
                
                # Generuj SQL INSERT
                table_name = self._table_name()
                column_names = self._column_names_for_insert()
                column_values = self._column_values_for_insert(item)
                
                query = f"INSERT INTO {table_name} ({column_names}) VALUES ({column_values})"
                logging.info(f"Executing query: {query}")
                
                cursor.execute(query)
                connection.commit()
                
                # Zwróć ID nowo wstawionego rekordu
                return cursor.lastrowid if cursor.lastrowid else 0
                
        except Error as err:
            logging.error(f"Database error: {err}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
        
        # Fallback return (nie powinno się nigdy wykonać)
        return 0

    # --------------------------------------------------------------------
    # Metody pomocnicze do generowania fragmentow SQL
    # --------------------------------------------------------------------

    def _table_name(self) -> str:
        return inflection.tableize(self._entity_type.__name__)

    def _field_names(self) -> list[str]:
        return self._entity().__dict__.keys()

    # name, age
    def _column_names_for_insert(self) -> str:
        fields = [field for field in self._field_names() if field.lower() != 'id_']
        return ', '.join(fields)

    # insert into teams (name, points) values ('A', 30)
    @classmethod
    def _column_values_for_insert(cls, item: Any) -> str:
        def to_str(entry: Any) -> str:
            return f"'{entry[1]}'" if isinstance(entry[1], (str, datetime, date)) else str(entry[1])

        return ', '.join([to_str(entry) for entry in item.__dict__.items() if entry[0].lower() != 'id_'])