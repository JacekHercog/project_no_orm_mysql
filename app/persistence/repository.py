from mysql.connector import Error
from typing import Any, Self
from mysql.connector.pooling import MySQLConnectionPool
from datetime import date, datetime
from app.persistence.model import Team, Player, PlayerWithTeamView
from dataclasses import dataclass
import inflection
import logging
from abc import ABC

# >> pipenv install inflection

logging.basicConfig(level=logging.INFO)


class CrudRepository(ABC):

    def __init__(self, connection_pool: MySQLConnectionPool, entity: Any):
        self._connection_pool = connection_pool
        self._entity = entity
        self._entity_type = type(entity())
        # self._create_tables()

    def insert(self, item: Any) -> int:
        with self._connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            sql = (f'insert into {self._table_name()} ({self._column_names_for_insert()}) '
                   f'values ({self._column_values_for_insert(item)})')
            cursor.execute(sql)
            conn.commit()
            return cursor.lastrowid

    # Albo przejdz na typ zwracany None albo mozesz zwracac list[int] id
    # elementow
    def insert_many(self, items: list[Any]) -> int:
        with self._connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            values = ", ".join([f'({CrudRepository._column_values_for_insert(item)})' for item in items])
            sql = (f'insert into {self._table_name()} ({self._column_names_for_insert()}) '
                   f'values {values}')
            cursor.execute(sql)
            conn.commit()
            return cursor.lastrowid

    def update(self, id_: int, item: Any) -> int:
        with self._connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            sql = f'update {self._table_name()} set {CrudRepository._column_names_and_values_for_update(item)} where id_={id_}'
            logging.info('***')
            logging.info(sql)
            logging.info('***')
            cursor.execute(sql)
            conn.commit()
            return id_

    def find_all(self) -> list[Any]:
        with self._connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            sql = f'select * from {self._table_name()}'
            cursor.execute(sql)
            return [self._entity(*row) for row in cursor.fetchall()]

    def find_by_id(self, id_: int) -> Any:
        with self._connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            sql = f'select * from {self._table_name()} where id_={id_}'
            cursor.execute(sql)
            return cursor.fetchone()

    def delete(self, id_: int) -> int:
        with self._connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            sql = f'delete from {self._table_name()} where id_={id_}'
            cursor.execute(sql)
            conn.commit()
            # TODO Czy mozna przechwycic id usunietego bytu
            return id_

    def delete_all(self) -> None:
        with self._connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            sql = f'delete from {self._table_name()} where id_>0'
            cursor.execute(sql)
            conn.commit()

    # --------------------------------------------------------------------
    # Metody pomocnicze do generowania fragmentow SQL
    # --------------------------------------------------------------------

    def _table_name(self) -> str:
        return inflection.tableize(self._entity_type.__name__)

    def _field_names(self) -> list[str]:
        # TODO Tutaj nastapilo rzutowanie do list i wczesniej tego nie bylo
        return list(self._entity().__dict__.keys())

    # name, age
    def _column_names_for_insert(self) -> str:
        fields = [field for field in self._field_names() if field.lower() != 'id_']
        return ', '.join(fields)

    @staticmethod
    def _to_str(value: Any) -> str:
        return f"'{value}'" if isinstance(value, (str, datetime, date)) else str(value)

    @staticmethod
    def _column_values_for_insert(item: Any) -> str:
        return ', '.join([CrudRepository._to_str(value) for field, value in item.__dict__.items() if field.lower() != 'id_'])

    @staticmethod
    def _column_names_and_values_for_update(item: Any) -> str:
        return ', '.join([
            f'{field}={CrudRepository._to_str(value)}'
            for field, value in item.__dict__.items()
            if field.lower() != 'id_' and value is not None
        ])

    # TODO [KRZYSZTOF MA TO POKAZAC] UWAGA!!!
    # Ta metoda tworzy tabele, ale jest tylko po to zebym mogl szybko utworzyc strukture DB, zeby
    # testowac repozytoria. Logika tworzenia tabel i zarzadzania ich struktura zostanie przeniesiona
    # do innej aplikacji

    # def _create_tables(self):
    #     with self._connection_pool.get_connection() as conn:
    #         cursor = conn.cursor()
    #
    #         teams_table_sql = '''
    #             create table if not exists teams (
    #                 id_ integer primary key auto_increment,
    #                 name varchar(50) not null,
    #                 points integer default 0
    #             );
    #         '''
    #
    #         players_table_sql = '''
    #             create table if not exists players (
    #                 id_ integer primary key auto_increment,
    #                 name varchar(50) not null,
    #                 goals integer default 0,
    #                 team_id integer,
    #                 foreign key (team_id) references teams(id_) on delete cascade on update cascade
    #             );
    #         '''
    #         cursor.execute(teams_table_sql)
    #         cursor.execute(players_table_sql)


class TeamRepository(CrudRepository):
    def __init__(self, connection_pool: MySQLConnectionPool):
        super().__init__(connection_pool, Team)

    # TeamRepository ma wszystkie metody z CrudRepository, ktore sa gotowe pracowac
    # z typem Team. Jezeli potrzebujesz jeszcze jakies dodatkowe metody konkretnie dla
    # Team, to piszesz jej w tym miejscu.

    def find_all_by_points_between(self, points_from: int, points_to: int) -> list[Team]:
        with self._connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            # sql injection
            sql = f'select * from teams t where t.points bewteen {points_from} and {points_to};'
            cursor.execute(sql)
            return [self._entity(*row) for row in cursor.fetchall()]

    def find_by_name(self, name: str) -> Team | None:
        with self._connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            # sql injection
            sql = f"select * from teams t where t.name = '{name}';"
            cursor.execute(sql)
            res = cursor.fetchone()
            return Team(*res) if res else res

class PlayerRepository(CrudRepository):
    def __init__(self, connection_pool: MySQLConnectionPool):
        super().__init__(connection_pool, Player)

# --------------------------------------------------------------------------------------

# Moze byc tak, ze masz w Twojej db konkretny widok np reprezentujacy graczy oraz ich druzyny
# Nie chcesz calego cruda tylko wygodna funkcjonalnosc pozwalajaca na pobranie danych z tego widoku
@dataclass
class PlayerWithTeamRepository:
    connection_pool: MySQLConnectionPool

    def find_all_players_with_teams(self, points_from: int, points_to: int) -> list[PlayerWithTeamView]:
        with self.connection_pool.get_connection() as conn:
            cursor = conn.cursor()
            return []

# --------------------------------------------------------------------------------------
# Repository, ktore moze zawierac nawet kilka metod wymagajacych wykonywania kilku operacji
# w jednej transakcji