import os
import sqlite3

# Database Names
if __debug__:
    LOGGING_DB="DB_Logging.db"
else:
    LOGGING_DB="DB_Logging_DEBUG.db"

CONNECTION_PATH=os.path.join(os.path.dirname(os.path.realpath(__file__)), "/Databases", LOGGING_DB)
USER_T="Users"
COMMANDS_T="Logs"
ERRORS_T="Errors"

#region "Database Initilization"
def CreateLoggingDB() -> None:
    """Initilizes the logging database.

        CREATE TABLE {USER_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            User TEXT NOT NULL,
            UserName TEXT NULL

        CREATE TABLE {COMMANDS_T}(
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            UserId INTEGER NOT NULL,
            Command TEXT NOT NULL,
            Arguments TEXT NULL,
            FOREIGN KEY(UserId) REFERENCES {USER_T}(Id)
    """    
    try:
        print("Create the logging DB started")
        conn = sqlite3.connect(CONNECTION_PATH)
        print(f"Connected to the {LOGGING_DB} database.")
        CreateUsersTable(conn)
        CreateCommandsTable(conn)
        CreateErrorTable(conn)
    except Exception as ex:
        print(f"Logging -- CreateLoggingDB -- {ex}")
    finally:
        conn.close()
        print(f"")

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
        print(f"{COMMANDS_T} table has been created in the {Conn}")
    except Exception as ex:
        print(f"Logging -- CreateLoggingTable -- {ex}")
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
        if(TableExists(Conn, USER_T)):
            return

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
        print(f"Logging -- CreateLoggingTable -- {ex}")
        Conn.rollback()
        raise ex

def CreateErrorsTable(Conn: sqlite3.Connection) -> None:
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
        if(TableExists(Conn, USER_T)):
            return

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
        print(f"Logging -- CreateLoggingTable -- {ex}")
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
        return (cur.rowcount == 1) 
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
        param = (user)
        cur = conn.execute(sql, param)
        result = (cur.rowcount == 1)

        if cur.rowcount > 1:
            raise Exception(f"Returned {cur.rowcount} rows.")

    except Exception as ex:
        print(f"Logging -- UserExist -- {ex}")
        raise ex

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
        if(UserExist == False):
            raise Exception("User doesn't exist.")

        conn = sqlite3.connect(CONNECTION_PATH)
        cur = conn.cursor()
        sql = f"SELECT Id FROM {USER_T} WHERE User=?"
        param = (user)
        data = cur.execute(sql, param)

        if(data.rowcount == 0):
            raise Exception("User doesn't exist.")

        if(data.rowcount > 1):
            raise Exception(f"User returned {data.rowcount} rows.")

        result = data[0][0]
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

def GetLogs(NumLogs: int = 5) -> list:
    """Gets the 5 most recent logs (or the number input).

    Args:
        NumLogs (int, optional): Number of logs to return. Defaults to 5.

    Returns:
        list: The rows returned from the select statement.
    """    
    try:
        if int < 1:
            raise Exception("Attempting to retrieve 0 or less records.")
    
        conn = sqlite3.connect(CONNECTION_PATH)
        cur = conn.cursor()
        result = cur.execute(f"SELECT * FROM {USER_T} LIMIT {NumLogs};")
    except Exception as ex:
        print(f"LOGGING -- GetLogs -- {ex}")
        result = []
    finally:
        conn.close()
        return result
    
#endregion

#region "Insert Commands"
def AddUser(user: str) -> int:
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
        
        conn = sqlite3.connect(CONNECTION_PATH)
        cur = conn.cursor()
        sql = f"""
                INSERT INTO {USER_T}(User)
                VALUES (?)
                RETURNING Id;
            """
        parameters = (user)
        data = cur.execute(sql, parameters)

        if(len(data) == 0):
            raise Exception("Insertion didn't return Id")
        
        result = cur.fetchone()[0]
        conn.commit()

    except Exception as ex:
        if (ex == Exception("User already exists")):
            result = GetUserId(User)
        else:
            result = -1
        conn.rollback()

    finally:
        conn.close()
        return result
    pass

def Command(User: str, Command: str, Args: str) -> None:
    """Adds a command log to the command log database.

    Args:
        User (str): The user's identification string.
        Command (str): The command the user used.
        Args (str): The arguments the user added.

    Raises:
        Exception: _description_
    """    
    try:
        conn = sqlite3.connect(CONNECTION_PATH)

        #Grabs the user id; if the user doesn't exist then add them.
        if(UserExist(User)):
            UserId = GetUserId
        else:
            UserId = AddUser(User)
        
        #Guard against adding a user returning -1
        if(UserId == -1):
            raise Exception("Grabbing User Id returned 0")
        
        cur = conn.cursor()
        sql = f"""
                INSERT INTO {USER_T}(UserId, Command, Arguements)
                VALUES (?, ?, ?);
            """
        param = (UserId, Command, Args)
        cur.execute(sql, param)
        conn.commit()
    except Exception as ex:
        print(f"Logging -- Log -- {ex}")
        conn.rollback
    finally:
        conn.close()

def Error(FileName: str, ):
    ...
#endregion

#region "Print commands"
def GetStringOfLog(LogId: int) -> str:
    try:
        assert type(LogId) == int, "LogId not int."

        conn = sqlite3.connect(CONNECTION_PATH)
        cur = conn.cursor()
        sql = f"SELECT * FROM {USER_T} WHERE Id={LogId};"
        data = cur.execute(sql)

        if(data.rowcount == 0):
            raise Exception("No data returned.")

        row = data[0]
        result = f"{GetUserId(row[2])} (Id: {row[2]}) ran {row[3]} at {row[1]} with {row[4]}"
    except Exception as ex:
        print(f"Logging -- Log -- {ex}")
        result = ""
    finally:
        conn.close()
        return result

def GetStringOfLogs(NumLogs: int = 5) -> list(str):
    try:
        Logs = GetLogs(NumLogs=NumLogs)
        result = []
        for Log in Logs:
            result.append(GetStringOfLog(Log[0]))
        return result
    except Exception as ex:
        print(f"Logging -- PrintLogs -- {ex}")

def PrintLogsToConsole(NumLogs: int = 5) -> None:
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