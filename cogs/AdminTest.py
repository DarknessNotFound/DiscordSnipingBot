# AdminTest.py

import discord
from discord.ext import commands

class AdminTest_Commands(commands.Cog):
    def __init__(self, client):
        self.client = client
    # Commands
    @commands.command(name='echo', help='Adds a snipe to the database')
    async def echo(self, ctx, *args):
        await ctx.send(' '.join(args))

async def setup(client):
    await client.add_cog(AdminTest_Commands(client))
