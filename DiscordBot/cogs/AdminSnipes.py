# AdminSnipes.py
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

class AdminSnipes(commands.Cog):
    def __init__(self, client):
        self.client = client
    # Commands
    @commands.command(name='snipes', help='''Shows snipe information.\nFlags
                      \t-a: All snipes,
                      \t-pid: All snipes related to a player's id,
                      \t-did: All snipes related to a player via @'ing them,
                      \t-sid: Snipe via the snipe id,
                      \t-sidr: Snipes ids within range (inclusive),
                      ''')
    async def Snipes(self, ctx, *args):
        """Shows the snipes in the database with various flag options.
        """        
        try:
            Log.Command(ctx.author.id, "snipes", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return

            GroupOfSnipes = []
            if len(args) == 0: # Most recent 5 snipes
                GroupOfSnipes.append(("5 Most Recent Snipes", DB.ReadSnipes()))

            elif args[0] == '-a': # All snipes.
                GroupOfSnipes.append(("All Snipes", DB.ReadAllSnipes()))

            elif args[0] == '-pid': # All snipes related to a player's id.
                if len(args) < 2:
                    await ctx.send("-pid requires 2 arguements, only 1 provided.")
                elif args[1].isdigit() == False:
                    await ctx.send("-pid requires an integer input for the player id.")
                elif DB.PlayerExistsId(int(args[1])) == False:
                    await ctx.send("Player not found.")
                else:
                    GroupOfSnipes.append(("Confirmed Kills", DB.ReadSnipesOfSniper(int(args[1]))))
                    GroupOfSnipes.append(("Victim", DB.ReadSnipesOfSniped(int(args[1]))))

            elif args[0] == '-did': # All snipes related to a player via @'ing them.
                PlayersDiscordId = DB.ExtractDiscordId(''.join(args))
                for DiscordId in PlayersDiscordId:
                    if DB.PlayerExistsDiscordId(DiscordId):
                        Player = DB.ReadPlayerDiscordId(DiscordId=DiscordId)
                        if len(Player) == 0:
                            await ctx.send(f"<@{DiscordId}> not found.")
                        else:
                            GroupOfSnipes.append((f"<@{Player[1]}>'s Confirmed Kills", DB.ReadSnipesOfSniper(Player[0])))
                            GroupOfSnipes.append((f"<@{Player[1]}>'s Deaths", DB.ReadSnipesOfSniped(Player[0])))
                    else:
                        await ctx.send(f"<@{DiscordId}> does not exists in the database.")

            elif args[0] == '-sid': # Snipes via their id.
                snipe = DB.ReadAllSnipes()
                if len(args) < 2:
                    await ctx.send("-sid requires 2 arguements, only 1 provided.")
                elif args[1].isdigit() == False:
                    await ctx.send("-pid requires an integer input for the player id.")
                GroupOfSnipes.append(("All Snipes", ))
            elif args[0] == '-sidr': # Snipes with ids (inclusive) within range.
                await ctx.send("WIP: this flag is still under construction.")
            else:
                if args[0].isdigit():
                    GroupOfSnipes.append((f"{args[0]} Most Recent Snipes", DB.ReadSnipes(int(args[0]))))
                else:
                    GroupOfSnipes.append(("5 Most Recent Snipes", DB.ReadSnipes()))

            for SnipeGroup in GroupOfSnipes:    
                msg = discord.Embed(
                    title=SnipeGroup[0]
                )

                count = 0
                if len(SnipeGroup[1]) == 0:
                    print(f"Title {SnipeGroup[0]} has no snipes.")
                    
                for snipe in SnipeGroup[1]:
                    count += 1
                    snipeString = SnipeToText(snipe=snipe)
                    msg.add_field(
                        name="",
                        value=snipeString,
                        inline=True
                    )
                    if count >= 24:
                        await ctx.send(embed=msg)
                        count = 0
                        msg.clear_fields()
                if count > 0:
                    await ctx.send(embed=msg)
            
            if len(GroupOfSnipes) == 0:
                await ctx.send("No snipes(s) found.")

        except Exception as ex:
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"Snipes\"")
            print(f"Message: {str(ex)}")
            Log.Error(FILE_NAME, "snipes", str(ex))

    @commands.command(name='addsnipe', help='Manual snipe >>addsnipe Sniper_Id Victum_Id')
    async def AddSnipe(self, ctx, *args):
        """Manually inserts a snipe into the database (records sniper and sniped)

        Args:
            ctx (_type_): 
        """        
        try:
            Log.Command(ctx.author.id, "addsnipe", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return
            
            await ctx.send("WIP: this command is still under construction.")

            if len(args) == 0:
                await ctx.send("ERROR: no arguements given, use >>help addsnipe for help.")
                return

        except Exception as ex:
            Log.Error(FILE_NAME, "AddSnipe", str(ex))

    @commands.command(name='removesnipe', help='Put the snipe id for each snipe to remove (space between each snipe id).')
    async def RemoveSnipe(self, ctx, *args):
        """Removes a snipe from the database.
        """
        try:
            Log.Command(ctx.author.id, "removesnipe", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return
            
            if len(args) == 0:
                await ctx.send("ERROR: no arguements given, use **>>help removesnipe** for help.")
                return
            
            results = []
            for id in args:
                if id.isdigit() == False:
                    MsgToSend = "Argument is not a digit."
                elif DB.SnipeIdExists(int(id)) == False:
                    MsgToSend = "Id not found in the database."
                else:
                    MsgToSend = DB.DeleteSnipe(id)
                results.append((str(id), MsgToSend))
            
            msg = discord.Embed(
                title="Snipes Removal"
            )

            count = 0
            for result in results:
                count += 1
                msg.add_field(
                    name=result[0],
                    value="Result: " + result[1],
                    inline=True
                )
                if count >= 24:
                    await ctx.send(embed=msg)
                    count = 0
                    msg.clear_fields()
            if count > 0:
                await ctx.send(embed=msg)

        except Exception as ex:
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"RemoveSnipe\"")
            print(f"Message: {str(ex)}")
            Log.Error(FILE_NAME, "RemoveSnipe", str(ex))

    @commands.command(name='undoremovesnipe', help='Put the snipe id for each snipe to remove (space between each snipe id).')
    async def UndoRemoveSnipe(self, ctx, *args):
        """Readds a snipe from the database.
        """
        try:
            Log.Command(ctx.author.id, "undoremovesnipe", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return
            
            if len(args) == 0:
                await ctx.send("ERROR: no arguements given, use **>>help removesnipe** for help.")
                return
            
            results = []
            for id in args:
                if id.isdigit() == False:
                    MsgToSend = "Argument is not a digit."
                else:
                    MsgToSend = DB.UndoDeleteSnipe(id)
                results.append((str(id), MsgToSend))
            
            msg = discord.Embed(
                title="Snipes Removal"
            )

            count = 0
            for result in results:
                count += 1
                msg.add_field(
                    name=result[0],
                    value="Result: " + result[1],
                    inline=True
                )
                if count >= 24:
                    await ctx.send(embed=msg)
                    count = 0
                    msg.clear_fields()
            if count > 0:
                await ctx.send(embed=msg)

        except Exception as ex:
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"RemoveSnipe\"")
            print(f"Message: {str(ex)}")
            Log.Error(FILE_NAME, "RemoveSnipe", str(ex))

    @commands.command(name='updatesnipe', help='>>updatesnipe [snipe ID] [sniper ID] [sniped ID]')
    async def UpdateSnipe(self, ctx, *args):
        """Updates a snipe in the database.
        """        
        try:
            Log.Command(ctx.author.id, "updatesnipe", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return
            
            await ctx.send("WIP: this command is still under construction.")

            if len(args) != 3:
                await ctx.send(f"ERROR: only {len(args)} arguements given but requires 3 arguements, use **>>help updatesnipe** for help.")
                return

        except Exception as ex:
            Log.Error(FILE_NAME, "UpdateSnipe", str(ex))
    #endregion

async def setup(client):
    await client.add_cog(AdminSnipes(client))
