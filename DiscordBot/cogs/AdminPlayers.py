# AdminPlayers.py
import discord
import Logging as Log
import DbManagement as DB
from discord.ext import commands

FILE_NAME = "AdminCommands"
ADMIN_PERMISSION_LEVEL = 1

def ExtractPlayerName(player: list) -> str:
    """Gets a playet's name based on the inputed player list.

    Args:
        player (list): Id, DiscordId, Name, Permissions, IsDeleted.

    Returns:
        str: The player's display name to be sent in discord.
    """
    if len(player) < 4:
        return ""
    
    if player[1] != "":
        return f"<@{player[1]}>"
    else:
        return player[2]

def SnipeToText(snipe: list) -> str:
    """Takes a given snipe list and converts it into printable discord text.

    Args:
        snipe (list): Id, Timestamp, sniperid, snipedid, isdeleted

    Returns:
        str: Printable string for discord.
    """
    if len(snipe) < 5:
        return ""
    SniperP = DB.ReadPlayerId(snipe[2])
    Sniper = ExtractPlayerName(SniperP)

    SnipedP = DB.ReadPlayerId(snipe[3])
    Sniped = ExtractPlayerName(SnipedP)

    return f">>> **Id**: {snipe[0]}\n**Timestamp**: {snipe[1]}\n**Sniper**: {Sniper}\n**Sniped**: {Sniped}"

class AdminPlayers(commands.Cog):
    def __init__(self, client):
        self.client = client
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
                    player = DB.ReadPlayerDiscordId(discordId)
                    if len(player) == 0:
                        await ctx.send(f"<@{discordId}> does not exists in the database.")
                    else:
                        PlayersToSend.append(player)
            
            if args[0] == '-a':
                PlayersToSend = DB.ReadAllPlayers()
            
            if args[0] == "-ad":
                PlayersToSend = DB.ReadAllDeletedPlayers()

            msg = discord.Embed(
                title="Player(s)"
            )

            if len(PlayersToSend) == 0:
                await ctx.send("No player(s) found.")
                return

            count = 0

            for p in PlayersToSend:
                Snipes = DB.CalcSnipes(p[0])
                Deaths = DB.CalcSniped(p[0])
                if p[1] == "": #If discord id is empty
                    playerString = ">>> **Id**: {}\n**Discord Id**: {}\n**Permission Level**: {}\n**Snipes**: {}\n**Deaths**: {}".format(p[0], p[1], p[3], Snipes, Deaths)
                else:
                    playerString = ">>> **Id**: {}\n**Discord Id**: <@{}>\n**Permission Level**: {}\n**Snipes**: {}\n**Deaths**: {}".format(p[0], p[1], p[3], Snipes, Deaths)
                msg.add_field(name=f"{p[2]}", value=playerString, inline=False)
                count += 1
                if count >= 24:
                    await ctx.send(embed=msg)
                    count = 0
                    msg.clear_fields()

            if count > 0:
                await ctx.send(embed=msg)

        except Exception as ex:
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"Players\"")
            print(f"Message: {str(ex)}")
            Log.Error(FILE_NAME, "Players", str(ex))

    @commands.command(name='addplayer', help='Enter a player into the database. Put a list of @mentions for adding via discord id or just their name for a single individual (although this can not add multiple)')
    async def AddPlayer(self, ctx, *args):
        """Manually adds a player to the database.
        """        
        try:
            Log.Command(ctx.author.id, "addplayer", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return
            
            if len(args) == 0:
                await ctx.send(f"ERROR: {len(args)} arguements given but at least 1 is required, use **>>help addplayer** for help.")
                return
            
            IdsCreated = []
            DiscordIds = DB.ExtractDiscordId(' '.join(args))
            if len(DiscordIds) > 0:
                for id in DiscordIds:
                    if(DB.PlayerExistsDiscordId(id)):
                        continue

                    User = await self.client.fetch_user(id)
                    SnipedName = User.display_name
                    IdsCreated.append(DB.CreatePlayer(DiscordId=id, Name=SnipedName))
            else:
                Name = ' '.join(args)
                IdsCreated.append(DB.CreatePlayer(Name=Name))
            
            PlayersToSend = []
            for id in IdsCreated:
                PlayersToSend.append(DB.ReadPlayerId(id))

            msg = discord.Embed(
                title="Player(s) Created"
            )

            count = 0
            for p in PlayersToSend:
                if p[1] == "": #If discord id is empty
                    playerString = ">>> **Id**: {}\n**Discord Id**: {}\n**Permission Level**: {}".format(p[0], p[1], p[3])
                else:
                    playerString = ">>> **Id**: {}\n**Discord Id**: <@{}>\n**Permission Level**: {}".format(p[0], p[1], p[3])
                msg.add_field(name=f"{p[2]}", value=playerString, inline=False)
                count += 1
                if count >= 24:
                    await ctx.send(embed=msg)
                    count = 0
                    msg.clear_fields()

            if len(PlayersToSend) == 0:
                await ctx.send("No player(s) added.")
            else:
                await ctx.send(embed=msg)

        except Exception as ex:
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"Players\"")
            print(f"Message: {str(ex)}")
            Log.Error(FILE_NAME, "AddPlayer", str(ex))

    @commands.command(name='rename', help='*>>rename [Player Id] [New Name]* Renames a player.')
    async def RenamePlayer(self, ctx, *args):
        """Updates a player's name in the database.
        """        
        try:
            Log.Command(ctx.author.id, "rename", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return
            
            await ctx.send("WIP: this command is still under construction.")

            if len(args) < 2:
                await ctx.send(f"ERROR: {len(args)} arguements given but at least 2 are required, use **>>help renameplayer** for help.")
                return
            
            PlayerId = args[0]
            if PlayerId.isdigit() == False:
                await ctx.send(f"ERROR: Player Id arguement must be a number, \"{args[0]}\" given.")
                return
            
            if DB.PlayerExistsId(PlayerId):
                Name = ' '.join(args[1:])
                Updated = DB.UpdatePlayerName(PlayerId, Name=Name)
                if Updated:
                    await ctx.send(f"User Id {PlayerId} name updated to \"{Name}\"")
                else:
                    await ctx.send("Error: Didn\'t update.")
            else:
                await ctx.send(f"Error: Player Id {PlayerId} does not exists.")

        except Exception as ex:
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"Players\"")
            print(f"Message: {str(ex)}")
            Log.Error(FILE_NAME, "RenamePlayer", str(ex))


async def setup(client):
    await client.add_cog(AdminPlayers(client))
