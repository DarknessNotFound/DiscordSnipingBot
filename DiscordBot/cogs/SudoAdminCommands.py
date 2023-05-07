# AdminTest.py
import discord
import Logging as Log
import DbManagement as DB
from discord.ext import commands

FILE_NAME = "SudoAdminCommands"
SUDO_PERMISSION_LEVEL = 2
ADMIN_PERMISSION_LEVEL = 1
PLAYER_PERMISSION_LEVEL = 0

class SudoAdmin(commands.Cog):
    def __init__(self, client):
        self.client = client
    # Commands
    @commands.command(name='UpdatePermission', help='updatepermission [@DiscordMention] [PermissionLevel]')
    async def UpdatePermission(self, ctx, *args):
        """Updates a players permission level. Must be their discord id then the permission level

        Args:
            ctx (_type_): _description_
        """        
        try:
            Log.Command(ctx.author.id, "UpdatePermission", ' '.join(args))
            if DB.AuthorHavePermission(ctx.author.id, SUDO_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return
            
            if len(args) != 2:
                await ctx.send("Have have exactly 2 arguements. Only " + str(len(args)) + " provided.")
                return
            
            DiscordId = DB.ExtractDiscordId(args[0])
            Level = args[1]

            if len(DiscordId) == 0:
                await ctx.send("Discord Id not valid")
                return
            
            if Level.isdigit() == False and Level != "-1":
                await ctx.send("Permission input isn't valid. Must be a number 0-9")
                return
            else:
                Level = int(Level)

            if int(Level) > 9:
                Level = 9

            Player = DB.ReadPlayerDiscordId(DiscordId=DiscordId[0])

            if len(Player) == 0:
                await ctx.send("Player not found.")
                return
            
            if Player[3] > 9:
                await ctx.send("You can't try to change the owners permission level")
                return
            
            if Level > -1:
                DB.UpdatePlayerPermissionLevel(Player[0], Level)
            else:
                DB.UpdatePlayerPermissionLevel(Player[0], -1)
            await ctx.send(f"Updated <@{DiscordId[0]}>'s permission level to {Level}")

        except Exception as ex:
            Log.Error(FILE_NAME, "Update Permission", str(ex))
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"Updatepermission\"")
            print(f"Message: {str(ex)}")
            await ctx.send("Error: An error has occured, please try again.")

    @commands.command(name='removeplayer', help='*>>rename [Player Id]* Removes a player from the database.')
    async def RemovePlayer(self, ctx, *args):
        """Removes a player from the database.
        """        
        try:
            Log.Command(ctx.author.id, "remove player", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, SUDO_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return
            
            PlayerId = args[0]
            if PlayerId.isdigit() == False:
                await ctx.send(f"ERROR: Player Id arguement must be a number, \"{args[0]}\" given.")
                return
            else:
                PlayerId = int(PlayerId)

            if DB.PlayerExistsId(PlayerId):
                PlayerPermissionLevel = DB.GetPermissionLevel(PlayerId)
                
                if PlayerPermissionLevel > 0:
                    await ctx.send("Can't remove a player with admin level permissions.")
                    return
                
                Updated = DB.DeletePlayer(PlayerId)
                await ctx.send(Updated)
            else:
                await ctx.send(f"Error: Player Id {PlayerId} does not exists.")

        except Exception as ex:
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"Players\"")
            print(f"Message: {str(ex)}")
            Log.Error(FILE_NAME, "RenamePlayer", str(ex))
            await ctx.send("ERROR: and error has occured.")

    @commands.command(name='undoremoveplayer', help='*>>rename [Player Id]* Removes a player from the database.')
    async def RemovePlayer(self, ctx, *args):
        """Undo removing player.
        """        
        try:
            Log.Command(ctx.author.id, "undo remove player", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, SUDO_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return
            
            PlayerId = args[0]
            if PlayerId.isdigit() == False:
                await ctx.send(f"ERROR: Player Id arguement must be a number, \"{args[0]}\" given.")
                return
            else:
                PlayerId = int(PlayerId)
                
            Updated = DB.UndoDeletePlayer(PlayerId)
            await ctx.send(Updated)

        except Exception as ex:
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"Players\"")
            print(f"Message: {str(ex)}")
            Log.Error(FILE_NAME, "RenamePlayer", str(ex))
            await ctx.send("ERROR: and error has occured.")


async def setup(client):
    await client.add_cog(SudoAdmin(client))
