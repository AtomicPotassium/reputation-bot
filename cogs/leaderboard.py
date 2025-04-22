# Importing modules

import disnake
from disnake.ext import commands
from pymongo import MongoClient
import os

# Setting up Class for `Unappreciated` Button

class Unappreciated(disnake.ui.Button):
    def __init__(self, bot: commands.Bot):
        """
            Intializing the button Object.
        """
        super().__init__(
            label="Most Unappreciated",
            emoji="📉",
            style=disnake.ButtonStyle.danger
        )

        self.bot = bot
    
    async def callback(self, inter: disnake.MessageInteraction):
        
        #Fetching Client Object to work with database.

        client = MongoClient(os.environ["M_URL"])

        db = client["AB_DB"]

        collect = db.get_collection("rating_level")

        top_ten = collect.find().sort("points", 1).limit(10) #Fetching top ten most unappreciated people

        #Declaring `desc` variable to make the actual leaderboard

        desc = ""


        #Iterating through the top_ten variable to fill desc
        for _, user in enumerate(top_ten, start=1):
            user_obj = await self.bot.fetch_user(user["user_id"])
            desc = desc + f"1. {user_obj.name} ({user["points"]} points)\n"

        #Initializing Embed & View

        embed = disnake.Embed(
            title="Leaderboard of top 10 unappreciated users:",
            description=desc
        )

        view = disnake.ui.View()

        view.add_item(Appreciated(self.bot))

        #Editing original message

        await inter.response.edit_message(embed=embed, view=view)

# Setting up Class for `Appreciated` Button

class Appreciated(disnake.ui.Button):

    """
        Intializing the button Object.
    """

    def __init__(self, bot: commands.Bot):
        super().__init__(
            label="Most Appreciated",
            emoji="📈",
            style=disnake.ButtonStyle.success
        )

        self.bot = bot
    
    async def callback(self, inter: disnake.MessageInteraction):

        #Fetching Client Object to work with database.

        client = MongoClient(os.environ["M_URL"])

        db = client["AB_DB"]

        collect = db.get_collection("rating_level")

        top_ten = collect.find().sort("points", -1).limit(10) #Fetching top ten most appreciated people

        #Declaring `desc` variable to make the actual leaderboard

        desc = ""

        #Iterating through the top_ten variable to fill desc
        for _, user in enumerate(top_ten, start=1):
            user_obj = await self.bot.fetch_user(user["user_id"])
            desc = desc + f"1. {user_obj.name} ({user["points"]} points)\n"

        #Initializing Embed & View

        embed = disnake.Embed(
            title="Leaderboard of top 10 appreciated users:",
            description=desc
        )

        view = disnake.ui.View()

        view.add_item(Unappreciated(self.bot))

        #Editing original message

        await inter.response.edit_message(embed=embed, view=view)

# Implementing Class for LeaderBoard Cog

class LeaderBoard(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def leaderboard(self, inter: disnake.ApplicationCommandInteraction):
        #Intializing Embed and View
        embed = disnake.Embed(
            title="Welcome to the leaderboards!",
            description="Click the type of leaderboard you want to see!"
        )

        view = disnake.ui.View()

        view.add_item(Appreciated(self.bot))
        view.add_item(Unappreciated(self.bot))

        #Sending message to user

        await inter.response.send_message(embed=embed, view=view, ephemeral=True)

# Setting Leaderboard Cog

def setup(bot: commands.Bot):
    bot.add_cog(LeaderBoard(bot))