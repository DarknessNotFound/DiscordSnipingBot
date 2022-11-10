# AdminTest.py
import discord
import Logging as Log
from discord.ext import commands

class AdminTest_Commands(commands.Cog):
    def __init__(self, client):
        self.client = client
    # Commands
    @commands.command(name='echo', help='Echos what user said.')
    async def echo(self, ctx, *args):
        Log.Command(ctx.author.name, "Echo", ' '.join(args))
        await ctx.send(' '.join(args))

async def setup(client):
    await client.add_cog(AdminTest_Commands(client))
