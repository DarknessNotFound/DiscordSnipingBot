# AdminTest.py
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


class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client
    # Commands

    @commands.command(name='quit', help='')
    async def players(self, ctx, *args):
        if not DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL):
            await ctx.send("Action denied: Not high enough permission level.")
            return
        raise RuntimeError("User quit the program")

    @commands.command(name='AdminRules', help='')
    async def DisplayRules(self, ctx, *args):
        if not DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL):
            await ctx.send("Action denied: Not high enough permission level.")
            return
        msg = discord.Embed(
                title="Welcome to the BSU's Fall 2023 Sniping Season",
                color=0xFF5733
                )
        msg.add_field(name="Motivation", inline=False, value="Hello, thanks for signing up for my EVIL internship. I, uhhh, need a someone who can aim my SNIPINATOR, Roger has been a pain in my side and I am ready to finish him once and FOR ALL! I tried aiming myself but I, uhhh, kinda missed. Sorry again Marge.")
        msg.add_field(name="Rules", inline=False, value="While I may be EVIL, my competitions don't have to be. This needs to be fair so that I can choose only the most EVIL sniper out there for my SNIPINATOR.")
        msg.add_field(name="Allowed Victims", inline=False, value="Only those who are an current member or alumni of the BSU may be sniped. Anyone can snipe Joebob off the streets but it is hard to snipe Perry the Platypus.")
        msg.add_field(name="DMZ", inline=False, value="The *Baptist Student Union Incorporated* is a DMZ zone. I don't want people sniping from the BSU Inc nor sniping into the BSU Inc. I live here ya know.")
        msg.add_field(name="Valid Snipes", inline=False, value="The snipes have to be obvious who was sniped, I don't have time to decipher all those pictures. I got inators to make.")
        msg.add_field(name="Questions", inline=False, value="Any questions or rules clarifications should be sent through Grant 1 or Grant 2. Those losers decided to help me with this FOR FREE, haha, its amazing what you can find off of the internet.")
        await ctx.send(embed=msg)

    # region Players
    @commands.command(name='players', help='Displays Players, use `>>players -h` for help')
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
                await ctx.send("ERROR: no arguements given, use >>players -h or >>help players for help.")
                return

            PlayersToSend = []
            if args[0] == "-h":
                msg = "## Players Command Help\n"
                msg += "* `-a` Gets all players\n"
                msg += "* `-ad` Gets all deleted players\n"
                msg += "* `-id [Player Id]` Gets a single player based on their id (must be an integer)\n"
                msg += "* -`-dis [@PEOPLE]` Gets the discord Id\n"

                await ctx.send(msg)
                return

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

            if args[0] == "-id":
                if len(args) == 1:
                    await ctx.send("Requires one id arguement, uses `>>players -h` for help")
                    return

                if not DB.PlayerExistsId(int(args[1])):
                    await ctx.send(f"Player id '{args[1]}' not found in the database")
                    return

                PlayersToSend = [DB.ReadPlayerId(int(args[1]))]

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
                if p[1] == "":  # If discord id is empty
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

            if len(args) < 2:
                await ctx.send(f"ERROR: {len(args)} arguements given but at least 2 are required, use **>>help renameplayer** for help.")
                return

            PlayerId = args[0]
            if not PlayerId.isdigit():
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
    # endregion

    # region Snipes

    @commands.command(name='snipes', help='Shows a list of all the snipes. Use `>>snipes -h` for help.')
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

            GroupOfSnipes = []
            if len(args) == 0:  # Most recent 5 snipes
                GroupOfSnipes.append(("5 Most Recent Snipes", DB.ReadSnipes()))

            elif args[0] == '-h':
                msg = "## Snipes Command Option\n"
                msg += "* `-h` gets the help command.\n"
                msg += "* `-a` gets all snipes\n"
                msg += "* `-pid [player id]` gets all the snipes of player. The ID must be an integer\n"
                msg += "* `-did [Discord mentions]` gets all the snipes of all the players mentioned.\n"
                msg += "* `-d [X]` Gets all the snipes from X days ago. X must be an integer.\n"
                msg += "* `-dr [X] [Y]` Gets all the snipes from X to Y days ago. X, Y must be an integer. X, Y are inclusive.\n"
                msg += "* `-sid [snipe id]` Gets a snipe based on its snipe id. Id must be an integer.\n"
                msg += "* `-sidr [start snipe id] [end snipe id]` Gets all the snipes from a range of ids. Id range is inclusive and must be integers\n"
                msg += "* `[X]` Gets the most recent X snipes. X must be an integer"

                await ctx.send(msg)
                return

            elif args[0] == '-a':  # All snipes.
                GroupOfSnipes.append(("All Snipes", DB.ReadAllSnipes()))

            elif args[0] == '-pid':  # All snipes related to a player's id.
                if len(args) < 2:
                    await ctx.send("-pid requires 2 arguements, only 1 provided.")
                elif not args[1].isdigit():
                    await ctx.send("-pid requires an integer input for the player id.")
                elif not DB.PlayerExistsId(int(args[1])):
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

            elif args[0] == '-d': # All snipes x days ago (default today).
                await ctx.send("WIP: this flag is still under construction.")
                days = 0

                if len(args) == 2:
                    days = 1
                else:
                    days = int(args[1])

            elif args[0] == '-dr':  # All snipes x to y days ago (default today or x to today).
                await ctx.send("WIP: this flag is still under construction.")

            elif args[0] == '-sid':  # Snipes via their id.
                await ctx.send("WIP: this flag is still under construction.")

            elif args[0] == '-sidr':  # Snipes with ids (inclusive) within range.
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
        except TypeError:
            await ctx.send("Please have integer inputs")
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
    # endregion

    # region Quotes

    @commands.command(name='addquote', help='>>insertquote [QUOTE TEXT]')
    async def InsertQuote(self, ctx, *args):
        """Inserts a new quote into the database.
        """
        try:
            Log.Command(ctx.author.id, "insertquote", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return

            if len(args) == 0:
                await ctx.send("No arguements added, aborting....")
                return

            if not DB.QualifiedQuote(' '.join(args)):
                await ctx.send("Not a valid quote; the quote needs \"<a>\" and \"<v>\".")
                return

            QuoteId = DB.CreateQuote(Quote=' '.join(args))
            await ctx.send(f"Inserted new quote, id {QuoteId} into the database")
            return

        except Exception as ex:
            Log.Error(FILE_NAME, "InsertQuote", str(ex))
            print(f"ERROR -- {FILE_NAME} -- InsertQuote: {ex}")

    @commands.command(name='quotes', help='>>quotes [-d, shows deleted quotes]')
    async def ReadQuotes(self, ctx, *args):
        """Inserts a new quote into the database.
        """
        try:
            Log.Command(ctx.author.id, "readquotes", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) is False:
                await ctx.send("Action denied: Not high enough permission level.")
                return

            if len(args) == 0:
                quotes = DB.ReadAllQuotes()
            else:
                if args[0] == "-d":
                    quotes = DB.ReadAllDeletedQuotes()
                else:
                    await ctx.send(f"Errror: expected \"-d\", recieved \"{args.join(' ')}\"")
                    quotes = []

            if len(quotes) == 0:
                await ctx.send("No quotes found")
                return

            msg = discord.Embed(
                title="Read Quotes"
            )

            count = 0
            for q in quotes:
                count += 1
                msg.add_field(
                    name=q[0],
                    value=f"{q[0]}: {q[1]}",
                    inline=True
                )
                if count >= 24:
                    await ctx.send(embed=msg)
                    count = 0
                    msg.clear_fields()
            if count > 0:
                await ctx.send(embed=msg)

        except Exception as ex:
            Log.Error(FILE_NAME, "ReadQuote", str(ex))
            print(f"ERROR -- {FILE_NAME} -- ReadQuote: {ex}")

    @commands.command(name='updatequote', help='>>updatequote [quote ID] [new quote]') 
    async def UpdateQuote(self, ctx, *args):
        """Updates a quote in the database.
        """        
        try:
            Log.Command(ctx.author.id, "updatequote", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return
            
            if len(args) < 2:
                await ctx.send(f"Needs at least 2 arguements, recieved {len(args)}.")
                return

            if args[0].isdigit() is False:
                await ctx.send(f"[ID] must be an positive integer, recieved \"{args[0]}\".")
                return

            if not DB.QuoteExists(int(args[0])):
                await ctx.send(f"Quote {args[0]} does not exists in the database.")
                return

            DB.UpdateQuote(int(args[0]), ' '.join(args[1:])) 
            quote = DB.GetQuote(args[0])
            await ctx.send(f"Updated snipe {args[0]} as \"{quote}\".")

        except Exception as ex:
            Log.Error(FILE_NAME, "UpdateSnipe", str(ex))

    @commands.command(name='deletequote', help='>>deletequote [quote ID]') 
    async def DeleteQuote(self, ctx, *args):
        """Deletes a quote in the database.
        """        
        try:
            Log.Command(ctx.author.id, "deletequote", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return

            if args[0].isdigit() is False:
                await ctx.send(f"[ID] must be an positive integer, recieved \"{args[0]}\".")
                return

            if not DB.QuoteExists(int(args[0])):
                await ctx.send(f"Quote {args[0]} does not exists in the database.")
                return

            result = DB.DeleteQuote(int(args[0]))
            await ctx.send(f"Result: {result}")

        except Exception as ex:
            Log.Error(FILE_NAME, "DeleteSnipe", str(ex))

    @commands.command(name='undodeletequote', help='>>undodeletequote [quote ID]') 
    async def UndoDeleteQuote(self, ctx, *args):
        """Deletes a quote in the database.
        """        
        try:
            Log.Command(ctx.author.id, "undodeletequote", ' '.join(args))

            if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
                await ctx.send("Action denied: Not high enough permission level.")
                return

            if args[0].isdigit() is False:
                await ctx.send(f"[ID] must be an positive integer, recieved \"{args[0]}\".")
                return

            result = DB.UndoDeleteQuote(int(args[0]))
            await ctx.send(f"Result: {result}")

        except Exception as ex:
            Log.Error(FILE_NAME, "UndoDeleteSnipe", str(ex))
    #endregion


async def setup(client):
    await client.add_cog(Admin(client))
