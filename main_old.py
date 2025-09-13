from app.persistence.connection import MySQLConnectionPoolBuilder

def main() -> None:
    connection_pool = MySQLConnectionPoolBuilder.builder().port(3307).user('user').build()

    # BEZ CONTEXT MANAGERA
    conn1 = connection_pool.get_connection()
    if conn1.is_connected():
        cursor = conn1.cursor()
        create_teams_sql = '''
                create table if not exists teams (
                    id integer primary key auto_increment,
                    name varchar(50) not null,
                    points integer default 0
                )
            '''
        cursor.execute(create_teams_sql)
        cursor.execute('show tables;')
        print(cursor.fetchall())

    # Z CONTEXT MANAGEREM
    with connection_pool.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("insert into teams (name, points) values ('A', 30)")
        # cursor.execute("insert into teams (name, points) values (10, 20, 30)")
        conn.commit()


# ---------------------------------------------------------------------------------
# Active Record
# ---------------------------------------------------------------------------------

# @dataclass
# class Person:
#     id_: int
#     name: str
#     age: int
#
#     def is_adult(self) -> bool:
#         return self.age >= 18
#
#     def save(self):
#         with connection_pool.get_connection() as conn:
#             cursor = conn.cursor()
#             cursor.execute("insert into poeple (name, age) values (?, ?)", (self.name, self.age))
#             conn.commit()
#
#     def delete(self):
#         pass
#
#     @classmethod
#     def find_by_id(cls, id_: int) -> Self:
#         pass
#
# p = Person('ADAM', 30)
# p.save()
# p.delete()
# p_from_db = Person.find_by_id(2)

if __name__ == '__main__':
    main()