# AdminTest.py
import discord
import Logging as Log
import DbManagement as DB
from discord.ext import commands

FILE_NAME = "PlayerCommands"
class Player_Commands(commands.Cog):
    def __init__(self, client):
        self.client = client
    # Commands
    @commands.command(name='snipe', help='Snipes the user, if possible please @ the person you sniped (and only the @)')
    async def snipe(self, ctx, *args):
        """The very basic snipe

        Args:
            ctx (_type_): _description_
        """        
        try:
            UserDiscordId = ctx.author.id
            SnipedName = ''.join(args)
            print(f"'{UserDiscordId}' sniped '{SnipedName}'")
            Log.Command(UserDiscordId, "snipe", ' '.join(args))
            
            if DB.PlayerExistsDiscordId(UserDiscordId):
                print("Here 1")
                SniperId = DB.ReadPlayerDiscordId(UserDiscordId)[0]
            else:
                print("Here 2")
                SniperId = DB.CreatePlayer(DiscordId=UserDiscordId, Name=ctx.author.display_name)
            
            if DB.PlayerExistsName(Name=SnipedName):
                print("Here 3")
                SnipedId = DB.ReadPlayerName(Name=SnipedName)[0]
            else:
                print("Here 4")
                SnipedId = DB.CreatePlayer(Name=SnipedName)

            SnipeId = DB.CreateSnipe(SniperId=SniperId, SnipedId=SnipedId)
            await ctx.send("Created snipe.")
        except Exception as ex:
            Log.Error(FILE_NAME, "snipe", str(ex))
            await ctx.send("Error recording sniping, please try again.")

async def setup(client):
    await client.add_cog(Player_Commands(client))
