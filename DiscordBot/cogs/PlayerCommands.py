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

            if DB.AuthorHavePermission(ctx.author.id, 0) == False:
                await ctx.send("Action denied: You've been banned nerd.")
                return

            #Get the sniped ID (creating if needed)
            for DiscordId in SnipedExtractedDiscordId:
                if DB.PlayerExistsDiscordId(DiscordId):
                    SnipedDbIds.append(DB.ReadPlayerDiscordId(DiscordId=DiscordId)[0])
                else:
                    SnipedUser = await self.client.fetch_user(DiscordId)
                    SnipedName = SnipedUser.display_name
                    SnipedDbIds.append(DB.CreatePlayer(DiscordId=DiscordId, Name=SnipedName))

            if len(SnipedExtractedDiscordId) == 0:
                NewName = ""
                for letter in SnipedArgs:
                    if letter != "@":
                        NewName += letter
                if DB.PlayerExistsName(Name=NewName):
                    SnipedDbIds.append(DB.ReadPlayerName(Name=NewName)[0])
                else:
                    SnipedDbIds.append(DB.CreatePlayer(Name=NewName))

            for SnipedId in SnipedDbIds:
                if SnipedId == SniperId:
                    await ctx.send("Stop hitting yourself! You cannot self-snipe.")
                    continue

                SnipeId = DB.CreateSnipe(SniperId=SniperId, SnipedId=SnipedId)
                await ctx.send(DB.GenerateSnipeString(SniperId, SnipedId))
        except Exception as ex:
            Log.Error(FILE_NAME, "snipe", str(ex))
            print(f"ERROR: In file \"{FILE_NAME}\" of command \"snipe\"")
            print(f"Message: {str(ex)}")
            await ctx.send("Error recording sniping, please try again.")

    @commands.command(name='rules', help='Sends out the rules of the game')
    async def rules(self, ctx, *args):
        """Prints the sniping rules.
        """        
        try:
            Log.Command(ctx.author.id, "rules", ' '.join(args))
            if DB.AuthorHavePermission(ctx.author.id, 0) == False:
                await ctx.send("Action denied: You've been banned nerd.")
                return
            msg = discord.Embed(
                title='Rules and Tutorial'
            )

            msg.add_field(
                name="***What is Sniping?***", 
                value="Sniping is taking photos of people without them noticing.", 
                inline=False)
            
            msg.add_field(
                name="***What is considered a valid snipe?***",
                value="For a snipe to count it has to be taken before the person being sniped sees you as well as..." +
                    "\n> **Clear**: the victim has to be clearly identifiable in the photo." +
                    "\n> - There is a little bit of grey area here." +
                    "\n\n> **BSU DMZ**: The BSU's (including the parking lot) is a \"No fire\" zone. You are NOT allowed to snipe from the BSU nor someone in the BSU." +
                    "\n\n> **Targets**: Only BSU members can be sniped, even if they aren't in the discord." +
                    "\n> - \"Active member\" will be up to the Grants' discretion." +
                    "\n\n> **Questionable Snipes**: If you question if your snipe is valid, do these two things: " +
                    "\n>   1. Ask the victim, if they agree it was a valid snipe, then generally it is okay to post without further action required." +
                    "\n>   2. If you don't know even after that, post it and send the snipe command, and then reply to your own post mentioning one of the Grants.",
                    inline=False                 
            )

            msg.add_field(
                name="***How to officially upload a snipe.***",
                value="1. Send the photo into the discord." +
                "\n2. Send the following command into the server" +
                "\n> >>snipe *Victim*" +
                "\n The victim must either mention the person being sniped using the @ or if they are NOT in the discord, you can use their first name and last initial." +
                "\n\n **Multi-snipes**" +
                "\n This year, we have a better bot that can handle snipes with multiple targets in them. You can now have multiple mentions in the *>>snipe* command. " +
                "However, for all victims NOT in the discord, still require multiple *>>snipe* commands for the bot to count them all."
            )

            await ctx.send(embed=msg)

        except Exception as ex:
            Log.Error(FILE_NAME, "rules", str(ex))
            await ctx.send("Error sending the rules, please try again.")   

async def setup(client):
    await client.add_cog(Player(client))
