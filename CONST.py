# This are all of the constants for the project

# Database Names
if __debug__:
    MainDB="DB_Snipes"
    LoggingDB="DB_Logging"
else:
    MainDB="DB_Snipes_DEBUG"
    LoggingDB="DB_Logging_DEBUG"

# Table Names
PlayersT="Players"
PlayersAlternateNamesT="PlayersAlternateNames"
SnipesT="Snipes"
PermT="Permissions"
LoggingT="Logs"