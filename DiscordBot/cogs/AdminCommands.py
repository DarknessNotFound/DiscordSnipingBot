# AdminTest.py
import discord
import Logging as Log
import DbManagement as DB
from discord.ext import commands

FILE_NAME = "AdminCommands"
ADMIN_PERMISSION_LEVEL = 1

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client
    # Commands
    @commands.command(name='players', help='Various Player Options: -dis for discord id, -id for id, -n for name, -a for all, and -ad for all deleted')
    async def players(self, ctx, *args):
        """list players

        Args:
            ctx (_type_): _description_
        """        
        try:
            Log.Command(ctx.author.id, "Players", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return
            
            if len(args) == 0:
                await ctx.send("ERROR: no arguements given, use >>help players for help.")
                return
            
            PlayersToSend = []
            if args[0] == "-dis" and len(args) > 1:
                DiscordIds = DB.ExtractDiscordId(' '.join(args[1:]))
                for discordId in DiscordIds:
                    PlayersToSend.append(DB.ReadPlayerDiscordId(discordId))
            
            if args [0] == '-a':
                PlayersToSend = DB.ReadAllPlayers()
            
            if args [0] == "-ad":
                PlayersToSend = DB.ReadAllDeletedPlayers()
            

            msg = discord.Embed(
                title="Player(s)"
            )
            
            if len(PlayersToSend) > 25:
                    count = 0
                    for p in PlayersToSend:
                        playerString = ">>> **Id**: {}\n**Discord Id**: <@{}>\n**Permission Level**: {}".format(p[0], p[1], p[3])
                        msg.add_field(name=f"{p[2]}", value=playerString, inline=False)
                        count += 1
                        if count >= 24:
                            await ctx.send(embed=msg)
                            count = 0
                            msg.clear_fields()
            else:
                for p in PlayersToSend:
                    playerString = ">>> **Id**: {}\n**Discord Id**: <@{}>\n**Permission Level**: {}".format(p[0], p[1], p[3])
                    msg.add_field(name=f"{p[2]}", value=playerString, inline=False)
                await ctx.send(embed=msg)
            
            if len(PlayersToSend) == 0:
                await ctx.send("No player(s) found.")

        except Exception as ex:
            Log.Error(FILE_NAME, "Players", str(ex))

    @commands.command(name='snipes', help='Shows a list of all the snipes.')
    async def Snipes(self, ctx, *args):
        """Shows the snipes in the database with various flag options.

        Args:
            ctx (_type_): 
        """        
        try:
            Log.Command(ctx.author.id, "snipes", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return
            
            await ctx.send("WIP: this command is still under construction.")

            send = 0
            if len(args) == 0: # Most recent 5 snipes
                send = 5
            elif args[0] == '-a': # All snipes.
                await ctx.send("WIP: this flag is still under construction.")
            elif args[0] == '-pid': # All snipes related to a player's id.
                await ctx.send("WIP: this flag is still under construction.")
            elif args[0] == '-did': # All snipes related to a player via @'ing them.
                await ctx.send("WIP: this flag is still under construction.")
            elif args[0] == '-d': # All snipes x days ago (default today).
                await ctx.send("WIP: this flag is still under construction.")
            elif args[0] == '-dr': # All snipes x to y days ago (default today or x to today).
                await ctx.send("WIP: this flag is still under construction.")
            elif args[0] == '-s': # Snipes via their id.
                await ctx.send("WIP: this flag is still under construction.")
            elif args[0] == '-sr': # Snipes with ids (inclusive) within range.
                await ctx.send("WIP: this flag is still under construction.")
            else:
                send = args[0]
                if not send.isdigit():
                    send = 5

            if send > 0:
                return
    
            

        except Exception as ex:
            Log.Error(FILE_NAME, "ManualSnipe", str(ex))

    @commands.command(name='mansnipe', help='Manual snipe >>mansnipe -a @sniper -d @sniped')
    async def ManualSnipe(self, ctx, *args):
        """Manually inserts a snipe into the database (records sniper and sniped)

        Args:
            ctx (_type_): 
        """        
        try:
            Log.Command(ctx.author.id, "mansnipe", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return
            
            await ctx.send("WIP: this command is still under construction.")

            if len(args) == 0:
                await ctx.send("ERROR: no arguements given, use >>help players for help.")
                return

        except Exception as ex:
            Log.Error(FILE_NAME, "ManualSnipe", str(ex))

async def setup(client):
    await client.add_cog(Admin(client))
