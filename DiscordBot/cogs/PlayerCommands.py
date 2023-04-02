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
            SnipedArgs = ''.join(args)
            Log.Command(UserDiscordId, "snipe", ' '.join(args))
            SnipedExtractedDiscordId = DB.ExtractDiscrodId(SnipedArgs)

            #Get the sniper ID (creating if needed)
            if DB.PlayerExistsDiscordId(UserDiscordId):
                print("Here 1")
                SniperId = DB.ReadPlayerDiscordId(UserDiscordId)[0]
            else:
                print("Here 2")
                SniperId = DB.CreatePlayer(DiscordId=UserDiscordId, Name=ctx.author.display_name)

            #Get the sniped ID (creating if needed)
            if len(SnipedExtractedDiscordId) == 18:
                if DB.PlayerExistsDiscordId(SnipedExtractedDiscordId):
                    print("Here 5")
                    SnipedId = DB.ReadPlayerDiscordId(SnipedExtractedDiscordId)[0]
                else:
                    print("Here 6")
                    SnipedUser = await self.client.fetch_user(SnipedExtractedDiscordId)
                    SnipedName = SnipedUser.display_name
                    SnipedId = DB.CreatePlayer(DiscordId=SnipedExtractedDiscordId, Name=SnipedName)
            else:
                if DB.PlayerExistsName(Name=SnipedArgs):
                    print("Here 3")
                    SnipedId = DB.ReadPlayerName(Name=SnipedArgs)[0]
                else:
                    print("Here 4")
                    SnipedId = DB.CreatePlayer(Name=SnipedArgs)

            SnipeId = DB.CreateSnipe(SniperId=SniperId, SnipedId=SnipedId)
            await ctx.send("Created snipe.")
        except Exception as ex:
            Log.Error(FILE_NAME, "snipe", str(ex))
            await ctx.send("Error recording sniping, please try again.")

async def setup(client):
    await client.add_cog(Player_Commands(client))
