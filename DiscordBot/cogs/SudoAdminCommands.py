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
            
            if Level.isdigit() == False:
                await ctx.send("Permission input isn't valid. Must be a number 0-9")
                return

            if int(Level) > 9:
                Level = 9

            Player = DB.ReadPlayerDiscordId(DiscordId=DiscordId[0])

            if len(Player) == 0:
                await ctx.send("Player not found.")
                return
            
            if Player[3] > 9:
                ctx.send("You can't try to change the owners permission level")
                return
            
            DB.UpdatePlayerPermissionLevel(Player[0], Level)
            await ctx.send(f"Updated <@{DiscordId[0]}>'s permission level to {Level}")

        except Exception as ex:
            Log.Error(FILE_NAME, "Players", str(ex))

async def setup(client):
    await client.add_cog(SudoAdmin(client))
