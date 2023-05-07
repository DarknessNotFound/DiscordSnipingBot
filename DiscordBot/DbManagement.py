import os
import sqlite3
import re
from CONST import *
import Logging as Log

# Database Names
if __debug__:
    SNIPES_DB="DB_Sniping_DEBUG.db"
else:
    SNIPES_DB="DB_Sniping.db"

CONNECTION_PATH=os.path.join("./Databases", SNIPES_DB)
PLAYERS_T="Players"
SNIPES_T="Snipes"
PERMISSIONS_T="Permissions"
ISOLATION_LEVEL="DEFERRED"

FILE_NAME="DbManagement"

#region "Helper"
def ExtractDiscordId(string: str) -> str:
    """Gets the discord id from the inputed string

    Args:
        string (str): string to extract from

    Returns:
        str: Empty if none are found, the discord id if that is found, and the original string if more than one is found.
    """
    pattern = "<@\d{18}>"
    patternIdOnly = "\d{18}"
    Canidates = re.findall(pattern, string)

    if len(Canidates) == 0:
        return []
    
    if len(Canidates) > 1:
        return [re.findall(patternIdOnly, Id)[0] for Id in Canidates]
    
    return [re.findall(patternIdOnly, Canidates[0])[0]]
#endregion

#region "Database Creation"
def CreateSnipesDB():
    """Creates all the databases nessessary for the program.
    """
    try:
        print("Creating the Sniping DB started.")
        conn = sqlite3.connect(CONNECTION_PATH)

        CreatePlayersTable(conn)
        CreateSnipesTable(conn)

    except Exception as ex:
        print(f"Logging -- CreateSnipesDB -- {ex}")
        Log.Error(FILE_NAME, "CreateSnipesDB", str(ex))
    finally:
        conn.close()

def CreatePlayersTable(Conn: sqlite3.Connection) -> None:
    """Creates the logging table tracking all users.

        CREATE TABLE {PLAYERS_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            DiscordId TEXT NULL,
            Name TEXT NULL,
            PermissionLevel INTEGER NOT NULL DEFAULT 0,
            IsDeleted INTEGER NOT NULL DEFAULT 0
        );
    Args:
        Conn (sqlite3.Connection): Connection to the database
    """    
    try:
        if(TableExists(Conn, PLAYERS_T)):
            return
        
        sql = f"""
        CREATE TABLE {PLAYERS_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            DiscordId TEXT NULL,
            Name TEXT NULL,
            PermissionLevel INTEGER NOT NULL DEFAULT 0,
            IsDeleted INTEGER NOT NULL DEFAULT 0
        );
        """
        Conn.execute(sql)
        Conn.commit()
        print(f"{PLAYERS_T} table has been created in the {Conn}")
    except Exception as ex:
        print(f"Logging -- CreatePlayersTable -- {ex}")
        Conn.rollback()
        raise ex

def CreateSnipesTable(Conn: sqlite3.Connection) -> None:
    """Creates the sniping table tracking who sniped who and when.

        CREATE TABLE {SNIPES_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            SniperId INTEGER NOT NULL,
            SnipedId INTEGER NOT NULL,
            IsDeleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(SniperId) REFERENCES {PLAYERS_T}(Id),
            FOREIGN KEY(SnipedId) REFERENCES {PLAYERS_T}(Id)
        );
    Args:
        Conn (sqlite3.Connection): Connection to the database
    """    
    try:
        if(TableExists(Conn, SNIPES_T)):
            return
        
        sql = f"""
        CREATE TABLE {SNIPES_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            SniperId INTEGER NOT NULL,
            SnipedId INTEGER NOT NULL,
            IsDeleted INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(SniperId) REFERENCES {PLAYERS_T}(Id),
            FOREIGN KEY(SnipedId) REFERENCES {PLAYERS_T}(Id)
            );
        """
        Conn.execute(sql)
        Conn.commit()
        print(f"{SNIPES_T} table has been created in the {Conn}")
    except Exception as ex:
        print(f"Logging -- CreateUsersTable -- {ex}")
        Conn.rollback()
        raise ex

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
        result = cur.fetchall()
        return len(result) == 1
    except Exception as ex:
        print(f"DbManagement -- TableExists -- {ex}")
        raise ex
#endregion

#region CRUD Testing
def TestingDbManagementCRUD():
    TestingPlayerCRUD()

def TestingPlayerCRUD():
    Id1 = CreatePlayer(DiscordId="1234",Name="Grant")
    Id2 = CreatePlayer(DiscordId="1111",Name="Pham")
    Id3 = CreatePlayer(DiscordId="2222",Name="Edwards")
    
    [print(element) for element in ReadPlayerId(Id3)]
    [print(element) for element in ReadPlayerId(Id2)]
    [print(element) for element in ReadPlayerId(Id1)]

    print(f"Id 1 Exists? {PlayerExistsId(1)}")
    print(f"Id 4 Exists? {PlayerExistsId(4)}")

    print()
    SnipeId1 = CreateSnipe(1, 3)
    print("Grant sniped Pham... Id: " + str(SnipeId1))
#endregion

#region "Create Commands"
def CreateSuperuser(DiscordId: str):
    """Creates a super user, this really should only be used once in main
    so that there is at least one user able to give others admin.

    Args:
        DiscordId (str): Their 18 digit discord id (only the numbers)
    """
    if PlayerExistsDiscordId(DiscordId=DiscordId):
        owner = ReadPlayerDiscordId(DiscordId=DiscordId)
        if len(owner) > 0:
            UpdatePlayerPermissionLevel(Id=owner[0], PermissionLevel=10)
    else:
        Id = CreatePlayer(DiscordId=DiscordId, Name="Owner")
        UpdatePlayerPermissionLevel(Id=Id, PermissionLevel=10)

def CreatePlayer(DiscordId: str = "", Name: str = "") -> int:
    """Adds a player by their discord id and/or their name.

    Args:
        DiscordId (str): The string to identify players, should be the ctx.author.id.
        User (str): This should either be their name or discord username.

    Raises:
        Exception: PlayerExists --> if the user already exists then doesn't add and just returns that user's id
        Exception: No data return --> The query didn't return a user id.

    Returns:
        int: The user id or -1 if there was an exception thrown.
    """    

    try:
        if DiscordId == "" and Name == "":
            raise Exception("Neither DiscordId nor Name inputed.")
        
        conn = sqlite3.connect(CONNECTION_PATH, isolation_level=ISOLATION_LEVEL)
        cur = conn.cursor()
        sql = f"""
                INSERT INTO {PLAYERS_T}(DiscordId, Name)
                VALUES (?, ?);
            """
        params = (DiscordId, Name)
        cur.execute(sql, params)
        conn.commit()
        if(cur.rowcount == 0):
            raise Exception("Insertion didn't return Id")
        
        result = cur.lastrowid

    except Exception as ex:
        print(f"{FILE_NAME} -- CreatePlayer -- {ex}")
        result = -1
        conn.rollback()

    finally:
        conn.close()
        return result

def CreateSnipe(SniperId: int, SnipedId: int) -> int:
    """Adds a player by their discord id and/or their name.

    Args:
        DiscordId (str): The string to identify players, should be the ctx.author.id.
        User (str): This should either be their name or discord username.

    Raises:
        Exception: PlayerExists --> if the user already exists then doesn't add and just returns that user's id
        Exception: No data return --> The query didn't return a user id.

    Returns:
        int: The user id or -1 if there was an exception thrown.
    """    

    try:
        if PlayerExistsId(Id=SniperId) == False:
            raise Exception("Sniper Id does not exists.")

        if PlayerExistsId(Id=SnipedId) == False:
            raise Exception("Sniped Id does not exists.")

        if SniperId == SnipedId:
            raise Exception("Cannot snipe yourself.")
        
        conn = sqlite3.connect(CONNECTION_PATH, isolation_level=ISOLATION_LEVEL)
        cur = conn.cursor()
        sql = f"""
                INSERT INTO {SNIPES_T}(SniperId, SnipedId)
                VALUES (?, ?);
            """
        params = (SniperId, SnipedId)
        cur.execute(sql, params)
        conn.commit()
        if(cur.rowcount == 0):
            raise Exception("Insertion didn't return Id")
        
        result = cur.lastrowid

    except Exception as ex:
        print(f"{FILE_NAME} -- CreateSnipe -- {ex}")
        result = -1
        conn.rollback()

    finally:
        conn.close()
        return result
#endregion

#region "Read Player Commands"
def PlayerExistsId(Id: int) -> bool:
    """Checks if a given Id exists in the players table

    Args:
        Id (Id): Id to check

    Raises:
        ex: Any error occurs

    Returns:
        bool: True if the table returns only one row
    """    
    try:
        result = False
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE Id=? AND IsDeleted=0"
        param = ([str(Id)])
        cur = conn.execute(sql, param)
        NumRows = len(cur.fetchall())
        result = NumRows == 1

        if cur.rowcount > 1:
            raise Exception(f"Returned {NumRows} rows.")

    except Exception as ex:
        print(f"{FILE_NAME} -- PlayerExistsId -- {ex}")
        raise ex

    finally:
        conn.close()
        return result

def PlayerExistsDiscordId(DiscordId: str) -> bool:
    """Checks if a given DiscordId exists in the players table

    Args:
        DiscordId (str): Id to check

    Raises:
        ex: Any error occurs

    Returns:
        bool: True if the table returns only one row
    """    
    try:
        result = False
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE DiscordId=? AND IsDeleted=0"
        param = ([str(DiscordId)])
        cur = conn.execute(sql, param)
        NumRows = len(cur.fetchall())
        result = NumRows != 0

        if cur.rowcount > 1:
            raise Exception(f"Returned {NumRows} rows.")

    except Exception as ex:
        print(f"{FILE_NAME} -- PlayerExistsDiscordId -- {ex}")
        raise ex

    finally:
        conn.close()
        return result

def PlayerExistsName(Name: str) -> bool:
    """Checks if a given DiscordId exists in the players table

        Args:
            DiscordId (str): Id to check

        Raises:
            ex: Any error occurs

        Returns:
            bool: True if the table returns only one row
    """    
    try:
        result = False
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE Name=? AND IsDeleted=0"
        param = ([str(Name)])
        cur = conn.execute(sql, param)
        NumRows = len(cur.fetchall())
        result = NumRows == 1

        if cur.rowcount > 1:
            raise Exception(f"Returned {NumRows} rows.")

    except Exception as ex:
        print(f"{FILE_NAME} -- PlayerExistsName -- {ex}")
        raise ex

    finally:
        conn.close()
        return result

def ReadPlayerId(Id: int) -> list:
    """Returns a list of a Player's properties.

    Args:
        Id (int): Player Id to return

    Returns:
        list: Id, DiscordId, Name, Permissions, IsDeleted
    """
    try:
        result = []
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE Id=?"
        param = ([str(Id)])
        cur = conn.execute(sql, param)
        row = cur.fetchone()
        result = list(row)
    except Exception as ex:
        Log.Error(FILE_NAME, "ReadPlayerId", str(ex))
    finally:
        conn.close()
        return result

def ReadPlayerDiscordId(DiscordId: str) -> list:
    """Returns a list of a Player's properties.

    Args:
        DiscordId (str): Player DiscordId to return

    Returns:
        list: Id, DiscordId, Name, Permissions, IsDeleted
    """
    try:
        result = []
        conn = sqlite3.connect(CONNECTION_PATH)
        if PlayerExistsDiscordId(DiscordId=DiscordId):
            sql = f"SELECT * FROM {PLAYERS_T} WHERE DiscordId=?"
            param = ([str(DiscordId)])
            cur = conn.execute(sql, param)
            row = cur.fetchone()
            result = list(row)
        else:
            print(f"Player DiscordId '{DiscordId}' does not exists.")
    except Exception as ex:
        Log.Error(FILE_NAME, "ReadPlayerDiscordId", str(ex))
    finally:
        conn.close()
        return result
    
def GetPermissionLevel(Id: int) -> int:
    """Returns the permission level of a given player Id.

    Args:
        Id (int): The player Id int the database.

    Returns:
        int: The permission level
    """
    try:
        result = 0
        conn = sqlite3.connect(CONNECTION_PATH)
        if PlayerExistsId(Id=Id):
            sql = f"SELECT * FROM {PLAYERS_T} WHERE Id=?;"
            param = (Id,)
            cur = conn.execute(sql, param)
            row = cur.fetchone()
            result = list(row)[3]
        else:
            print(f"Player Id:{Id} does not exists.")
    except Exception as ex:
        Log.Error(FILE_NAME, "ReadPlayerDiscordId", str(ex))
    finally:
        conn.close()
        return result
    
def CalcSnipes(Id: int) -> int:
    try:
        result = 0
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {SNIPES_T} WHERE SniperId=?;"
        param = (Id,)
        cur = conn.execute(sql, param)
        row = cur.fetchall()
        result = len(list(row))
    except Exception as ex:
        Log.Error(FILE_NAME, "CalcSnipes", str(ex))
    finally:
        conn.close()
        return result

def CalcSniped(Id: int) -> int:
    try:
        result = 0
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {SNIPES_T} WHERE SnipedId=?;"
        param = (Id,)
        cur = conn.execute(sql, param)
        row = cur.fetchall()
        result = len(list(row))
    except Exception as ex:
        Log.Error(FILE_NAME, "CalcSniped", str(ex))
    finally:
        conn.close()
        return result


def ReadPlayerName(Name: str) -> list:
    """Returns a list of a Player's properties.

    Args:
        Name (str): Player Name to return

    Returns:
        list: Id, DiscordId, Name, Permissions, IsDeleted
    """
    try:
        result = []
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE Name=?;"
        param = ([str(Name)])
        cur = conn.execute(sql, param)
        row = cur.fetchone()
        result = list(row)
    except Exception as ex:
        Log.Error(FILE_NAME, "ReadPlayerDiscordId", str(ex))
    finally:
        conn.close()
        return result

def ReadAllPlayers() -> list:
    result = []
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE IsDeleted=0;"
        cur = conn.execute(sql)
        rows = cur.fetchall()

        for row in rows:
            result.append(list(row))
        
    except Exception as ex:
        Log.Error(FILE_NAME, "ReadAllPlayers", str(ex))
        result = []
    finally:
        conn.close()
        return result

def ReadAllDeletedPlayers() -> list:
    result = []
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {PLAYERS_T} WHERE IsDeleted=1;"
        cur = conn.execute(sql)
        rows = cur.fetchall()

        for row in rows:
            result.append(list(row))
        
    except Exception as ex:
        Log.Error(FILE_NAME, "ReadAllPlayers", str(ex))
        result = []
    finally:
        conn.close()
        return result

def AuthorHavePermission(DiscordId, PermissionLevel):
    player = ReadPlayerDiscordId(DiscordId)
    if len(player) < 4:
        return False
    else:
        return PermissionLevel <= player[3]

def PlayerDisplayName(Id: int) -> str:
    if PlayerExistsId(Id=Id):
        player = ReadPlayerId(Id=Id)
        if len(player) == 0:
            return ""
        
        #If player doesn't have a DiscordId then display name
        if player[1] == "":
            return player[2]
        #Otherwise show their discord name.
        else:
            return f"<@{player[1]}>"

    else:
        return ""
#endregion

#region "Read Snipes Commands"
def SnipeIdExists(Id: int) -> bool:
    """Checks if a given Id exists in the snipes table

    Args:
        Id (Id): Id to check

    Raises:
        ex: Any error occurs

    Returns:
        bool: True if the table returns only one row
    """    
    try:
        result = False
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {SNIPES_T} WHERE Id=? AND IsDeleted=0;"
        param = (Id,)
        cur = conn.execute(sql, param)
        NumRows = len(cur.fetchall())
        result = NumRows == 1

        if cur.rowcount > 1:
            raise Exception(f"Returned {NumRows} rows.")

    except Exception as ex:
        print(f"{FILE_NAME} -- SnipeIdExists -- {ex}")
        result = False

    finally:
        conn.close()
        return result

def ReadSnipes(NumSnipes: int = 5) -> list:
    """Gets the 5 most recent snipes from the snipe table (or the number input).

    Args:
        NumLogs (int, optional): Number of logs to return. Defaults to 5.

    Returns:
        list: The rows returned from the select statement.
    """    
    try:
        result = []
        if NumSnipes < 1:
            raise Exception("Attempting to retrieve 0 or less records.")
    
        conn = sqlite3.connect(CONNECTION_PATH)
        cur = conn.cursor()
        data = cur.execute(f"SELECT * FROM {SNIPES_T} WHERE IsDeleted=0 ORDER BY Timestamp DESC LIMIT {NumSnipes};").fetchall()
        result = [list(row) for row in data]
    except Exception as ex:
        print(f"{FILE_NAME} -- ReadSnipes -- {ex}")
        result = []
    finally:
        conn.close()
        return result
    
def ReadAllSnipes() -> list:
    result = []
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {SNIPES_T} WHERE IsDeleted=0;"
        cur = conn.execute(sql)
        rows = cur.fetchall()

        for row in rows:
            result.append(list(row))
        
    except Exception as ex:
        Log.Error(FILE_NAME, "ReadAllPlayers", str(ex))
        result = []
    finally:
        conn.close()
        return result

def ReadSnipesOfSniper(SniperId: int):
    result = []
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {SNIPES_T} WHERE IsDeleted=0 AND SniperId=?;"
        param = (SniperId,)
        cur = conn.execute(sql, param)
        rows = cur.fetchall()

        for row in rows:
            result.append(list(row))

    except Exception as ex:
        Log.Error(FILE_NAME, "ReadSnipesOfSniper", str(ex))
        result = []
    finally:
        conn.close()
        return result
    
def ReadSnipesOfSniped(SnipedId: int):
    result = []
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {SNIPES_T} WHERE IsDeleted=0 AND SnipedId=?;"
        param = (SnipedId,)
        cur = conn.execute(sql, param)
        rows = cur.fetchall()

        for row in rows:
            result.append(list(row))

    except Exception as ex:
        Log.Error(FILE_NAME, "ReadSnipesOfSniped", str(ex))
        result = []
    finally:
        conn.close()
        return result
#endregion

#region "Update Commands"
def UpdatePlayerDiscordId(Id: int, DiscordId: str) -> None:
    return

def UpdatePlayerName(Id: int, Name: str):
    Updated = False
    if PlayerExistsId(Id=Id) == False:
        return False
    
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"UPDATE {PLAYERS_T} SET Name=? WHERE Id=?;"
        param = (Name, Id)
        conn.execute(sql, param)
        conn.commit()
        Updated = True
    except Exception as ex:
        print("Error in UpdatePlayerPermissionLevel: " + str(ex))
        Log.Error(FILE_NAME, "UpdatePlayerPermissionLevel", str(ex))
    finally:
        conn.close()
        return Updated

def UpdatePlayerPermissionLevel(Id: int, PermissionLevel: int):
    Updated = False
    if PlayerExistsId(Id=Id) == False:
        return False
    
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"UPDATE {PLAYERS_T} SET PermissionLevel=? WHERE Id=?"
        param = (PermissionLevel, Id)
        conn.execute(sql, param)
        conn.commit()
        Updated = True
    except Exception as ex:
        print("Error in UpdatePlayerPermissionLevel: " + str(ex))
        Log.Error(FILE_NAME, "UpdatePlayerPermissionLevel", str(ex))
    finally:
        conn.close()
        return Updated


#endregion

#region "Delete Commands"
def DeletePlayer(Id: int) -> str:
    Updated = "Didn't update."
    if PlayerExistsId(Id=Id) == False:
        return "Snipe Id doesn't exists."
    
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"UPDATE {PLAYERS_T} SET IsDeleted=1 WHERE Id=?;"
        param = (Id,)
        conn.execute(sql, param)
        conn.commit()
        Updated = f"Removed player of id \"{Id}\" from the database."
    except Exception as ex:
        print(f"ERROR: In file \"{FILE_NAME}\" of function \"DeleteSnipe\"")
        print(f"Message: {str(ex)}")
        Log.Error(FILE_NAME, "Remove player", str(ex))
        Updated = "ERROR: An error has occured..."
    finally:
        conn.close()
        return Updated

def UndoDeletePlayer(Id: int) -> str:
    Updated = "Didn't update."
    
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"UPDATE {PLAYERS_T} SET IsDeleted=0 WHERE Id=?;"
        param = (Id,)
        conn.execute(sql, param)
        conn.commit()
        Updated = f"Readded player of id \"{Id}\" from the database."
    except Exception as ex:
        print(f"ERROR: In file \"{FILE_NAME}\" of function \"DeleteSnipe\"")
        print(f"Message: {str(ex)}")
        Log.Error(FILE_NAME, "Remove player", str(ex))
        Updated = "ERROR: An error has occured..."
    finally:
        conn.close()
        return Updated

def DeleteSnipe(Id: int) -> str:
    Updated = "Didn't update."
    if SnipeIdExists(Id=Id) == False:
        return "Snipe Id doesn't exists."
    
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"UPDATE {SNIPES_T} SET IsDeleted=1 WHERE Id=?;"
        param = (Id,)
        conn.execute(sql, param)
        conn.commit()
        Updated = f"Removed snipe of id \"{Id}\" from the database."
    except Exception as ex:
        print(f"ERROR: In file \"{FILE_NAME}\" of function \"DeleteSnipe\"")
        print(f"Message: {str(ex)}")
        Log.Error(FILE_NAME, "Remove snipe", str(ex))
        Updated = "ERROR: An error has occured..."
    finally:
        conn.close()
        return Updated
    
def UndoDeleteSnipe(Id: int) -> str:
    Updated = "Didn't update."
    
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"UPDATE {SNIPES_T} SET IsDeleted=0 WHERE Id=?;"
        param = (Id,)
        conn.execute(sql, param)
        conn.commit()
        Updated = f"Readded snipe of id \"{Id}\" from the database."
    except Exception as ex:
        print(f"ERROR: In file \"{FILE_NAME}\" of function \"DeleteSnipe\"")
        print(f"Message: {str(ex)}")
        Log.Error(FILE_NAME, "Undo Remove snipe", str(ex))
        Updated = "ERROR: An error has occured..."
    finally:
        conn.close()
        return Updated
#endregion