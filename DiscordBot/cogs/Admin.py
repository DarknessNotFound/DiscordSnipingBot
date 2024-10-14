# Admin.py
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
        if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
            await ctx.send("Action denied: Not high enough permission level.")
            return
        raise RuntimeError("User quit the program")

    @commands.command(name='AdminRules', help='')
    async def DisplayRules(self, ctx, *args):
        if DB.AuthorHavePermission(ctx.author.id, ADMIN_PERMISSION_LEVEL) == False:
            await ctx.send("Action denied: Not high enough permission level.")
            return
        msg = discord.Embed(
                title="Welcome to the BSU's Fall 2024 Sniping Season",
                color=0xFF5733
                )
        msg.add_field(name="Motivation", inline=False, value="Ruh-roh-Raggy! Scooby snacks are not worth monsters. Rello, rould you snipe ronsters for me? I only have enough Scooby snacks for one sniper.")
        msg.add_field(name="Rules", inline=False, value="We want a fair fight and will unmask any cheaters caught in our little competition -Velma")
        msg.add_field(name="Allowed Victims", inline=False, value="Only those who are an current member or alumni of the BSU may be sniped. Anyone can snipe Joebob off the streets but it is hard to snipe the Fredster. -Fred")
        msg.add_field(name="DMZ", inline=False, value="The *Baptist Rudent Runion* is a DMZ zone. I don't want people sniping from the BSU nor sniping into the BSU.")
        msg.add_field(name="Valid Snipes", inline=False, value="The snipes have to be obvious who was sniped, I don't have time to decipher all those pictures man. I got sandwiches to make. -Shaggy")
        msg.add_field(name="Questions", inline=False, value="Any questions or rules clarifications should be sent to Grant 2, he is doing it for a scooby snack. - Daphne")
        await ctx.send(embed=msg)

    #region Quotes
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
