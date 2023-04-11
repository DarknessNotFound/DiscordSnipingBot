# AdminTest.py
import discord
import Logging as Log
from discord.ext import commands

FILE_NAME = "LoggingCommands"

class Logging(commands.Cog):
    def __init__(self, client):
        self.client = client

    # Commands
    @commands.command(name='logs', help='Gets the x most recent logs; x is an integer with a default of 5.')
    async def GetCommandLogs(self, ctx, *args):
        """
        Gets the most recent log commands from the database and sends them as a formated embed.
        """
        try:
            Logs = []
            if len(args) > 0:
                if args[0].isdigit():
                    Logs = Log.GetCommandLogs(int(args[0]))
                else:
                    await ctx.send("Amount is not an integer and thus undeterminable. Showing 5 most recent logs.")
                    Logs = Log.GetCommandLogs()
            else:
                Logs = Log.GetCommandLogs()
            if Logs is None:
                await ctx.send("No data found.")
                return

            embed = discord.Embed(
                title=f"Command Logs"
            )

            for log in Logs:
                logString = ">>> **Id**: {}\n**Timestamp**: {}\n**UserId**: {}\n**Command**: {}\n**Arguments**: {}".format(log[0], log[1], log[2], log[3], log[4])
                embed.add_field(name="", value=logString, inline=False)
            await ctx.send(embed=embed)
        except Exception as ex:
            print(f"{FILE_NAME}, error-commands, {ex}")
            Log.Error(FILE_NAME, "log-commands", str(ex))
        
    @commands.command(name='errors', help='Gets the x most recent logs; x is an integer with a default of 5.')
    async def GetErrors(self, ctx, *args):
        """
        Gets the most recent errors from the database and sends them as a formated embed.
        """
        try:
            await ctx.send("Fetching Errors.")
            
            Errors = []
            if len(args) > 0:
                if args[0].isdigit():
                    Errors = Log.GetErrorLogs(int(args[0]))
                else:
                    await ctx.send("Amount is not an integer and thus undeterminable. Showing 5 most recent logs.")
                    Errors = Log.GetErrorLogs()
            else:
                Errors = Log.GetErrorLogs()
            if Errors is None:
                await ctx.send("No data found.")
                return

            embed = discord.Embed(
                title=f"Error Logs"
            )

            for e in Errors:
                ErrorString = ">>> **Id**: {}\n**Timestamp**: {}\n**File**: {}\n**Function**: {}\n**Message**: {}".format(e[0], e[1], e[2], e[3], e[4])
                embed.add_field(name="", value=ErrorString, inline=False)
            await ctx.send(embed=embed)
        except Exception as ex:
            print(f"{FILE_NAME}, error-commands, {ex}")
            Log.Error(FILE_NAME, "error-commands", str(ex))

async def setup(client):
    await client.add_cog(Logging(client))
