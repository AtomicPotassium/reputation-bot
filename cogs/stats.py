import disnake
from disnake.ext import commands
from pymongo import MongoClient
import os

# Implementing Class for Global stats Button
class GlobalStats(disnake.ui.Button):
    def __init__(self, bot: commands.Bot):

        """
            Initializing Global Stats button object.
        """

        super().__init__(
            label="Global Stats",
            emoji="🌎",
            style=disnake.ButtonStyle.success
        )

        self.bot = bot
    
    async def callback(self, inter: disnake.MessageInteraction):

        #Fetching user_id through Custom ID

        user_id = int(self.custom_id[1:])
        
        user = await self.bot.fetch_user(user_id)

        # Implementing Client object to work with database.

        client = MongoClient(os.environ["M_URL"])

        db = client["AB_DB"]

        collect = db.get_collection("rating_level")

        # Fetching all cards to find total reputation

        cards = collect.find({"user_id": user_id})

        rep = 0

        # Adding all the points to the rep variables

        for card in cards:
            rep += card["points"]
        
        # Implementing Embed and View

        embed = disnake.Embed(
            title=f"{user.name}'s profile",
            description=f"**Reputation:** {rep}",
            color=disnake.Colour.green()
        )

        embed.set_thumbnail(user.default_avatar)

        view = disnake.ui.View()

        GS_OBJ = GlobalStats(self.bot)

        GS_OBJ.disabled = True    

        SS_OBJ = ServerStats(self.bot)

        SS_OBJ.custom_id = "S" + str(user_id)

        view.add_item(SS_OBJ)

        view.add_item(GS_OBJ)

        # Responding to the user

        await inter.response.edit_message(embed=embed, view=view)

# Implementing Class for Server stats Button
class ServerStats(disnake.ui.Button):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            label="Server Stats",
            emoji="🏠",
            style=disnake.ButtonStyle.blurple
        )

        self.bot = bot
    
    async def callback(self, inter: disnake.MessageInteraction):

        #Fetching user_id through Custom ID and user object through ID

        user_id = int(self.custom_id[1:])
        
        user = await self.bot.fetch_user(user_id)

        # Implementing Client object to work with database.

        client = MongoClient(os.environ["M_URL"])

        db = client["AB_DB"]

        collect = db.get_collection("rating_level")

        # Fetching the card of the server.
        card = collect.find_one({"user_id": user_id, "guild_id": inter.guild.id})

        # Setting the rep variable to the amount of points the user has obtained from the server, if the user hasn't been found in the card, then rep is set to 0
        try:
            rep = card["points"]
        except:
            rep = 0
        
        # Implementing Embed and View

        embed = disnake.Embed(
            title=f"{user.name}'s profile",
            description=f"**Reputation:** {rep}",
            color=disnake.Colour.blurple()
        )

        embed.set_thumbnail(user.default_avatar)

        view = disnake.ui.View()

        SS_OBJ = ServerStats(self.bot)

        SS_OBJ.disabled = True

        GS_OBJ = GlobalStats(self.bot)

        GS_OBJ.custom_id = f"G{user_id}"

        view.add_item(GS_OBJ)

        view.add_item(SS_OBJ)

        # Responding to the user

        await inter.response.edit_message(embed=embed, view=view)

# Implementing Stats Command Cog
class StatsCommand(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def stats(self, inter: disnake.ApplicationCommandInteraction, target: disnake.User):
        
        #Initializing Embed and View

        embed = disnake.Embed(
            title="Welcome to the stats!",
            description="Click the type of stats of the user you want to see!"
        )

        view = disnake.ui.View()

        SS_OBJ = ServerStats(self.bot)

        SS_OBJ.custom_id = "S" + str(target.id)

        GS_OBJ = GlobalStats(self.bot)

        GS_OBJ.custom_id = "G" + str(target.id)

        view.add_item(SS_OBJ)

        view.add_item(GS_OBJ)

        # Responding to the user

        await inter.response.send_message(embed=embed, view=view, ephemeral=True)
    
# Setting up the StatsCommand Cog
def setup(bot: commands.Bot):
    bot.add_cog(StatsCommand(bot))