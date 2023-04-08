# AdminTest.py
import discord
import Logging as Log
import DbManagement as DB
from discord.ext import commands

FILE_NAME = "PlayerCommands"
class Player(commands.Cog):
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
            SnipedArgs = ' '.join(args)
            Log.Command(UserDiscordId, "snipe", ' '.join(args))
            SnipedExtractedDiscordId = DB.ExtractDiscordId(SnipedArgs)
            SnipedDbIds = []
                
            #Get the sniper ID (creating if needed)
            if DB.PlayerExistsDiscordId(UserDiscordId):
                SniperId = DB.ReadPlayerDiscordId(UserDiscordId)[0]
            else:
                SniperId = DB.CreatePlayer(DiscordId=UserDiscordId, Name=ctx.author.display_name)

            #Get the sniped ID (creating if needed)
            for DiscordId in SnipedExtractedDiscordId:
                if DB.PlayerExistsDiscordId(DiscordId):
                    SnipedDbIds.append(DB.ReadPlayerDiscordId(DiscordId)[0])
                else:
                    SnipedUser = await self.client.fetch_user(DiscordId)
                    SnipedName = SnipedUser.display_name
                    SnipedDbIds.append(DB.CreatePlayer(DiscordId=DiscordId, Name=SnipedName))

            if len(SnipedExtractedDiscordId) == 0:
                if DB.PlayerExistsName(Name=SnipedArgs):
                    SnipedDbIds.append(DB.ReadPlayerName(Name=SnipedArgs)[0])
                else:
                    SnipedDbIds.append(DB.CreatePlayer(Name=SnipedArgs))

            for SnipedId in SnipedDbIds:
                if SnipedId == SniperId:
                    await ctx.send("Stop hitting yourself! You cannot self-snipe.")
                    continue

                SnipeId = DB.CreateSnipe(SniperId=SniperId, SnipedId=SnipedId)
                await ctx.send(f"{DB.PlayerDisplayName(SniperId)} sniped {DB.PlayerDisplayName(SnipedId)} -- Snipe Id: {SnipeId}")
        except Exception as ex:
            Log.Error(FILE_NAME, "snipe", str(ex))
            await ctx.send("Error recording sniping, please try again.")

async def setup(client):
    await client.add_cog(Player(client))
