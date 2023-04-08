import os
import sqlite3
from time import sleep
from discord.ext.commands import Context

# Database Names
if __debug__:
    LOGGING_DB="DB_Logging_DEBUG.db"
else:
    LOGGING_DB="DB_Logging.db"

CONNECTION_PATH=os.path.join("./Databases", LOGGING_DB)
USER_T="Users"
COMMANDS_T="Logs"
ERRORS_T="Errors"
ISOLATION_LEVEL="DEFERRED"

#region "Database Initilization"
def CreateLoggingDB() -> None:
    """Initilizes the logging database.

        CREATE TABLE {USER_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            User TEXT NOT NULL,
            UserName TEXT NULL

        CREATE TABLE Logs(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            UserId INTEGER NOT NULL,
            Command TEXT NOT NULL,
            Arguments TEXT NULL,
            FOREIGN KEY(UserId) REFERENCES Users(Id)

        CREATE TABLE {ERRORS_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            File INTEGER NOT NULL,
            Function TEXT NOT NULL,
            Message TEXT NOT NULL,
    """    
    try:
        print("Creating the Logging DB started.")
        conn = sqlite3.connect(CONNECTION_PATH)

        CreateUsersTable(conn)
        CreateCommandsTable(conn)
        CreateErrorsTable(conn)
    except Exception as ex:
        print(f"Logging -- CreateLoggingDB -- {ex}")
    finally:
        conn.close()

def CreateUsersTable(Conn: sqlite3.Connection) -> None:
    """Creates the logging table that keeps track of users running
       commands.

        CREATE TABLE {USER_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            User TEXT NOT NULL,
            UserName TEXT NULL
    Args:
        Conn (sqlite3.Connection): Connection to the database
    """    
    try:
        if(TableExists(Conn, USER_T)):
            return
        
        sql = f"""
        CREATE TABLE {USER_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            User TEXT NOT NULL,
            UserName TEXT NULL,
            IsDeleted INTEGER NOT NULL DEFAULT 0
        );
        """
        Conn.execute(sql)
        Conn.commit()
        print(f"{USER_T} table has been created in the {Conn}")
    except Exception as ex:
        print(f"Logging -- CreateUsersTable -- {ex}")
        Conn.rollback()
        raise ex

def CreateCommandsTable(Conn: sqlite3.Connection) -> None:
    """Creates the logging table that keeps track of users running
       commands.

        CREATE TABLE {COMMANDS_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            UserId INTEGER NOT NULL,
            Command TEXT NOT NULL,
            Arguments TEXT NULL,
            FOREIGN KEY(UserId) REFERENCES {USER_T}(Id)

    Args:
        Conn (sqlite3.Connection): Connection to the database
    """    
    try:
        if(TableExists(Conn, USER_T) == False):
            raise Exception("User table doesn't exist.")

        if(TableExists(Conn, COMMANDS_T)):
            return
        
        sql = f"""
        CREATE TABLE {COMMANDS_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            UserId INTEGER NOT NULL,
            Command TEXT NOT NULL,
            Arguements TEXT NULL,
            FOREIGN KEY(UserId) REFERENCES {USER_T}(Id)
        );
        """
        Conn.execute(sql)
        Conn.commit()
        print(f"{COMMANDS_T} table has been created in the {Conn}")
    except Exception as ex:
        print(f"Logging -- CreateCommandsTable -- {ex}")
        Conn.rollback()
        raise ex

def CreateErrorsTable(Conn: sqlite3.Connection) -> None:
    """Creates the error logging table that keeps track of any errors.

        CREATE TABLE {ERRORS_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            File INTEGER NOT NULL,
            Function TEXT NOT NULL,
            Message TEXT NOT NULL,
  
    Args:
        Conn (sqlite3.Connection): Connection to the database
    """    
    try:
        if(TableExists(Conn, ERRORS_T)):
            return
        
        sql = f"""
        CREATE TABLE {ERRORS_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            File INTEGER NOT NULL,
            Function TEXT NOT NULL,
            Message TEXT NOT NULL
        );
        """
        Conn.execute(sql)
        Conn.commit()
        print(f"{ERRORS_T} table has been created in the {Conn}")
    except Exception as ex:
        print(f"Logging -- CreateErrorsTable -- {ex}")
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
        print(f"LOGGING -- TableExists -- {ex}")
        raise ex
#endregion

#region "Read Commands"
def UserExist(user: str) -> bool:
    """Checks if the user exists in the database

    Args:
        user (str): User identification string

    Raises:
        ex: Any error occurs

    Returns:
        bool: If the table returns only one row
    """    
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        sql = f"SELECT * FROM {USER_T} WHERE User=?"
        param = ([user])
        cur = conn.execute(sql, param)
        NumRows = len(cur.fetchall())
        result = NumRows == 1

        if cur.rowcount > 1:
            raise Exception(f"Returned {NumRows} rows.")

    except Exception as ex:
        print(f"Logging -- UserExist -- {ex}")
        raise ex
        result = False
    finally:
        conn.close()
        return result

def GetUserId(user: str) -> int:
    """Gets the Id based on the user's identification string.

    Args:
        user (str): User's identification string.

    Returns:
        int: User's id.
    """    
    try:
        if(UserExist(user) == False):
            raise Exception("User doesn't exist.")

        conn = sqlite3.connect(CONNECTION_PATH)
        cur = conn.cursor()
        sql = f"SELECT Id FROM {USER_T} WHERE User=?"
        param = ([user])
        cur.execute(sql, param)
        rows = cur.fetchall()

        if(len(rows) == 0):
            raise Exception("User doesn't exist.")

        if(len(rows) > 1):
            raise Exception(f"User returned {rows.rowcount} rows.")

        result = rows[0][0]
    except Exception as ex:
        print(f"Logging -- GetUserId -- {ex}")
        raise ex
    finally:
        conn.close()
        return result

def GetUserName(id: int) -> str:
    """Gets the user's name based off of their id in the database.

    Args:
        id (int): The user's id as in the users table

    Returns:
        str: User's name.
    """    
    return "User Name Placeholder."

def GetCommandLogs(NumLogs: int = 5) -> list:
    """Gets the 5 most recent logs from the command table (or the number input).

    Args:
        NumLogs (int, optional): Number of logs to return. Defaults to 5.

    Returns:
        list: The rows returned from the select statement.
    """    
    try:
        result = []
        if NumLogs < 1:
            raise Exception("Attempting to retrieve 0 or less records.")
    
        conn = sqlite3.connect(CONNECTION_PATH)
        cur = conn.cursor()
        data = cur.execute(f"SELECT * FROM {COMMANDS_T} ORDER BY Timestamp DESC LIMIT {NumLogs};").fetchall()
        result = [list(row) for row in data]
    except Exception as ex:
        print(f"LOGGING -- GetLogs -- {ex}")
        result = []
    finally:
        conn.close()
        return result
    
def GetErrorLogs(NumLogs: int = 5) -> list:
    """Gets the 5 most recent logs from the error table (or the number input).

    Args:
        NumLogs (int, optional): Number of logs to return. Defaults to 5.

    Returns:
        list: The rows returned from the select statement.
    """    
    try:
        result = []
        if NumLogs < 1:
            raise Exception("Attempting to retrieve 0 or less records.")
    
        conn = sqlite3.connect(CONNECTION_PATH)
        cur = conn.cursor()
        data = cur.execute(f"SELECT * FROM {ERRORS_T} ORDER BY Timestamp DESC LIMIT {NumLogs};").fetchall()
        result = [list(row) for row in data]
    except Exception as ex:
        print(f"LOGGING -- GetErrorLogs -- {ex}")
        result = []
    finally:
        conn.close()
        return result
#endregion

#region "Insert Commands"
def AddUser(user: str, *args) -> int:
    """Adds a user by their "user" name (instead of their actual name).

    Args:
        User (str): The string to identify users (should be the ctx.author.name if using in a discord bot).

    Raises:
        Exception: UserExists --> if the user already exists then doesn't add and just returns that user's id
        Exception: No data return --> The query didn't return a user id.

    Returns:
        int: The user id or -1 if there was an exception thrown.
    """    
    try:
        if(UserExist(user)):
            raise Exception("User already exists")
        
        conn = sqlite3.connect(CONNECTION_PATH, isolation_level=ISOLATION_LEVEL)
        cur = conn.cursor()
        sql = f"""
                INSERT INTO {USER_T}(User)
                VALUES (?);
            """
        params = (user,)
        cur.execute(sql, params)
        conn.commit()
        if(cur.rowcount == 0):
            raise Exception("Insertion didn't return Id")
        
        result = cur.lastrowid

    except Exception as ex:
        print(f"Logging -- AddUser -- {ex}")
        if (ex == Exception("User already exists")):
            result = GetUserId(user)
        else:
            result = -1
        conn.rollback()

    finally:
        conn.close()
        return result

def Command(User: str, Command: str, Args: str) -> None:
    """Adds a command log to the command log database.

    Args:
        User (str): The user's identification string.
        Command (str): The command the user used.
        Args (str): The arguments the user added.

    """    
    try:
        conn = sqlite3.connect(CONNECTION_PATH)

        #Grabs the user id; if the user doesn't exist then add them.
        if(UserExist(User)):
            UserId = GetUserId(User)
        else:
            UserId = AddUser(User)
        
        #Guard against adding a user returning -1
        if(UserId == -1):
            raise Exception("Grabbing User Id returned -1")
        
        cur = conn.cursor()
        sql = f"""
                INSERT INTO {COMMANDS_T}(UserId, Command, Arguements)
                VALUES (?, ?, ?);
            """
        param = (UserId, Command, Args)
        cur.execute(sql, param)
        conn.commit()
    except Exception as ex:
        print(f"Logging -- Command -- {ex}")
        conn.rollback
    finally:
        conn.close()

def Error(FileName: str, Function: str, ErrorMsg: str) -> None:
    """Adds an error log to the error table.

    Args:
        FileName (str): The file name that contains the function.
        Command (str): The command that caused the error.
        ErrorMsg (str): The error message.
    """     
    try:
        conn = sqlite3.connect(CONNECTION_PATH)
        cur = conn.cursor()
        sql = f"""
                INSERT INTO {ERRORS_T}(File, Function, Message)
                VALUES (?, ?, ?);
            """
        param = (FileName, Function, ErrorMsg)
        cur.execute(sql, param)
        conn.commit()
    except Exception as ex:
        print(f"Logging -- Error -- {ex}")
        conn.rollback
    finally:
        conn.close()
#endregion

#region "Print Command Logs"
def GetStringOfCommandLog(Log):
    """Takes a row from the commands table and converts it into a string to read.

    Args:
        Log (RowFromCommandDatabase): Row from the commands database.

    Returns:
        str: Printable string version of the row.
    """    
    try:
         return f"{GetUserId(Log[2])} (Id: {Log[2]}) ran {Log[3]} at {Log[1]} with {Log[4]}"
    except Exception as ex:
        print(f"Logging -- GetStringOfCommandLog -- {ex}")
        return ""

def GetStringOfCommandLogs(NumLogs: int = 5):
    try:
        Logs = GetCommandLogs(NumLogs=NumLogs)
        result = []
        for Log in Logs:
            result.append(GetStringOfCommandLog(Log))
        return result
    except Exception as ex:
        print(f"Logging -- GetStringOfCommandLogs -- {ex}")

def PrintCommandLogsToConsole(NumLogs: int = 5) -> None:
    """Prints to the console all of the logs based on the number of logs inputed.

    Args:
        NumLogs (int, optional): Number of logs to output. Defaults to 5.
    """    
    try:
        Logs_S = GetStringOfCommandLogs(NumLogs=NumLogs)
        for string in Logs_S:
            print(string)
    except Exception as ex:
        print(f"Logging -- PrintLogs -- {ex}")
#endregion

#region "Print Error Logs"
def GetStringOfErrorLog(Log) -> str:
    try:
        return f"{GetUserId(Log[2])} (Id: {Log[2]}) ran {Log[3]} at {Log[1]} with {Log[4]}"
    except Exception as ex:
        print(f"Logging -- GetStringOfErrorLog -- {ex}")
        return ""

def GetStringOfErrorLogs(NumLogs: int = 5):
    try:
        Logs = GetErrorLogs(NumLogs=NumLogs)
        result = []
        for Log in Logs:
            result.append(GetStringOfLog(Log))
        return result
    except Exception as ex:
        print(f"Logging -- PrintLogs -- {ex}")
        return []

def PrintErrorLogsToConsole(NumLogs: int = 5) -> None:
    """Prints to the console all of the logs based on the number of logs inputed.

    Args:
        NumLogs (int, optional): Number of logs to output. Defaults to 5.
    """    
    try:
        Logs_S = GetStringOfLogs(NumLogs=NumLogs)
        for string in Logs_S:
            print(string)
    except Exception as ex:
        print(f"Logging -- PrintLogs -- {ex}")
#endregion
