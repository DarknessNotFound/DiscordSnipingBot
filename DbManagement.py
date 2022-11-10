import sqlite3
from CONST import *
import Logging as Log

def CreateSnipesDB():
    return
    conn = sqlite3.connect(CONST.MainDB)
    CreatePlayersTable(conn)
    CreateSnipesTable(conn)
    CreatePermissionsTable(conn)

def CreatePlayersTable(Conn):
    pass

def CreatePlayersAlternateNamesTable(Conn):
    pass

def CreateSnipesTable(Conn):
    pass

def CreatePermissionsTable(Conn):
    pass

def TableExists(Conn: sqlite3.Connection, Table: str) -> bool:
    """Checks wether a table exists or not in the given database.

    Args:
        Conn (sqlite3.Connection): The database connection to check.
        Table (str): The name of the table.

    Returns:
        bool: True if the table exists; False otherwise.
    """    
    try:
        sql = f"""SELECT name 
              FROM sqlite_master 
              WHERE type='table' 
              AND name='{Table}';"""
        cur = Conn.execute(sql)
        return (cur.rowcount == 1) 
    except Exception as ex:
        print(f"DbManagement -- TableExists -- {ex}")
        return False
