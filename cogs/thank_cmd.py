# Importing modules

import disnake
from disnake.ext import commands
from datetime import datetime
from pymongo import MongoClient
import os

# Implementing ThankCommand Cog
class ThankCommand(commands.Cog):

    def __init__(self, bot: commands.Bot):
        # Initialization of bot
        self.bot = bot
    
    # Intialization of /appreciate command
    @commands.slash_command()
    async def appreciate(self, inter: disnake.ApplicationCommandInteraction, target: disnake.User):

        #Fetching Client Object to work with database.

        client = MongoClient(os.environ["M_URL"])

        db = client["AB_DB"]
        
        collect = db.get_collection("cooldown_list")

        exists = collect.find_one({"user_id": inter.user.id, "guild_id": inter.guild.id})

        """
            Checking if the user is on cooldown-list collection
            If they are and their cooldown hasn't expired yet then to return a message and terminate the command action
            If they are and their cooldown has expired then delete the card and continue with the command action
        """

        if exists:
            if exists["cooldown"] > datetime.now().timestamp():
                await inter.response.send_message(f"You're not allowed to appreciate/unappreciate yet! You will be able to appreciate/unappreciate in: <t:{round(exists["cooldown"])}:f>", ephemeral=True)
                return
            else:
                collect.delete_one({"user_id": inter.user.id, "guild_id": inter.guild.id})

        # Checking if the user is trying to appreciate themselves.

        if target.id == inter.user.id:
            await inter.response.send_message("You're not allowed to appreciate yourself!", ephemeral=True)
            return

        # Fetching target's discord ID

        target_id = target.id
        
        """
            Fetching rating_level collection to check if the target exists in the collection (If they don't, then creating a new card for the user.)
            Adding 1 point to the target's point.
        """

        collect = db.get_collection("rating_level")

        exists = collect.find_one({"user_id": target_id})
        
        if not exists:
            collect.insert_one({"user_id": target_id, "guild_id": inter.guild.id, "points": 0})
        
        points = collect.find_one({"user_id": target_id})["points"]

        collect.update_one({"user_id": target_id}, {"$set": {"points": points + 1}})

        # Implementing cooldown for the user who triggered the command.

        collect = db.get_collection("cooldown_list")

        collect.insert_one({"user_id": inter.user.id, "guild_id": inter.guild.id, "cooldown": datetime.now().timestamp() + 600})

        # Attempting to send message to the target, if the operation fails then a warning is sent in the terminal.

        try:
            await target.send(f"A user has just appreciated you! Now you have: `{points + 1}` points!")
        except:
            print("Failed to send message to user!")
        
        # Sending response to user.

        await inter.response.send_message(f"Thank you for appreciating {target.mention}!", ephemeral=True)

    # Intialization of /appreciate command
    @commands.slash_command()
    async def unappreciate(self, inter: disnake.ApplicationCommandInteraction, target: disnake.User):
        
        #Fetching Client Object to work with database.

        client = MongoClient(os.environ["M_URL"])

        db = client["AB_DB"]
        
        collect = db.get_collection("cooldown_list")

        exists = collect.find_one({"user_id": inter.user.id, "guild_id": inter.guild.id})

        """
            Checking if the user is on cooldown-list collection
            If they are and their cooldown hasn't expired yet then to return a message and terminate the command action
            If they are and their cooldown has expired then delete the card and continue with the command action
        """

        if exists:
            if exists["cooldown"] > datetime.now().timestamp():
                await inter.response.send_message(f"You're not allowed to appreciate/unappreciate yet! You will be able to appreciate/unappreciate in: <t:{round(exists["cooldown"])}:f>", ephemeral=True)
                return
            else:
                collect.delete_one({"user_id": inter.user.id, "guild_id": inter.guild.id})

        # Checking if the user is trying to unappreciate themselves.

        if target.id == inter.user.id:
            await inter.response.send_message("You're not allowed to unappreciate yourself!", ephemeral=True)

        target_id = target.id

        """
            Fetching rating_level collection to check if the target exists in the collection (If they don't, then creating a new card for the user.)
            Subtracting 1 point from the target's point.
        """

        collect = db.get_collection("rating_level")

        exists = collect.find_one({"user_id": target_id})
        
        if not exists:
            collect.insert_one({"user_id": target_id, "guild_id": inter.guild.id, "points": 0})
        
        points = collect.find_one({"user_id": target_id})["points"]

        collect.update_one({"user_id": target_id}, {"$set": {"points": points - 1}})

        # Implementing cooldown for the user who triggered the command.

        collect = db.get_collection("cooldown_list")

        collect.insert_one({"user_id": inter.user.id, "guild_id": inter.guild.id, "cooldown": datetime.now().timestamp() + 600})

        # Attempting to send message to the target, if the operation fails then a warning is sent in the terminal.

        try:
            await target.send(f"A user has just unappreciated you! Now you have: `{points - 1}` points!")
        except:
            print("Failed to send message to user!")
        
        # Sending response to user.
        await inter.response.send_message(f"Thank you for unappreciating {target.mention}!\n\n**Note**: If they have said anything against Discord TOS we would kindly request you to report them!", ephemeral=True)

# Setting up ThankCommand Cog
def setup(bot: commands.Bot):
    bot.add_cog(ThankCommand(bot))