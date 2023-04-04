# AdminTest.py
import discord
import Logging as Log
import DbManagement as DB
from discord.ext import commands

FILE_NAME = "AdminCommands"
class Admin_Commands(commands.Cog):
    def __init__(self, client):
        self.client = client
    # Commands
    @commands.command(name='players', help='Various Player Options: -dis for discord id, -id for id, -n for name, -a for all, and -ad for all deleted')
    async def echo(self, ctx, *args):
        """Echos

        Args:
            ctx (_type_): _description_
        """        
        try:
            Log.Command(ctx.author.id, "Players", ' '.join(args))
            print(args)
            if len(args) == 0:
                await ctx.send("ERROR: no arguements given, use >>help players for help.")
                return
            
            PlayersToSend = []
            if args[0] == "-dis" and len(args) > 1:
                DiscordId = DB.ExtractDiscrodId(args[1])
                if DiscordId == "":
                    return
            
            if args [0] == '-a':
                print("Displaying all players")
                PlayersToSend = DB.ReadAllPlayers()
            
            if args [0] == "-ad":
                PlayersToSend = DB.ReadAllDeletedPlayers()
            

            msg = discord.Embed(
                title="Player(s)"
            )
            
            if len(PlayersToSend) > 25:
                await ctx.send("WIP ERROR: more than 25 players and embed breaks but this has not been fixed yet.")
            else:
                for p in PlayersToSend:
                    playerString = ">>> **Id**: {}\n**Discord Id**: {}\n**Permission Level**: {}".format(p[0], p[1], p[3])
                    msg.add_field(name=f"{p[2]}", value=playerString, inline=False)
            
            if len(PlayersToSend) == 0:
                await ctx.send("No player(s) found.")
            else:
                await ctx.send(embed=msg)

        except Exception as ex:
            Log.Error(FILE_NAME, "Players", str(ex))

async def setup(client):
    await client.add_cog(Admin_Commands(client))
