import discord, json, os
from discord import app_commands
from discord.ext import commands, tasks
from discord.ui import TextInput, Modal

from methods.database import User
from methods.database import Database

from methods.vinted import Vinted

class FilterModal(Modal):
    def __init__(self):
        super().__init__(title="Set Item Name & Filter Link")
        self.filter_name = TextInput(label="Item Name" , placeholder="Enter your item name here")
        self.filter_link = TextInput(label="Filter Link", placeholder="Enter your filter link here", required=True)
        self.add_item(self.filter_name)
        self.add_item(self.filter_link)

    async def on_submit(self, interaction: discord.Interaction):
        filter_name = self.filter_name.value
        filter_link = self.filter_link.value + f"&search_text=" +f"{filter_name}".replace(" " , "%20")
        
        db = Database('database/vinted_db.db')
        user = User(id=interaction.user.id , name=interaction.user.name , filter_link=filter_link , filter_name=filter_name)
        db.update_user(user=user)

        await interaction.response.send_message(f'Item Name Set To: {filter_name}\nFilter Link Set To: {filter_link}', ephemeral=True)

class Tracker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.listing_sender.start()

    def cog_unload(self):
        self.listing_sender.cancel()

    def get_all_file_names(self, folder_path: str) -> list[str]:
        try:
            file_names = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            return file_names
        except FileNotFoundError:
            print(f"The folder '{folder_path}' does not exist.")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    @tasks.loop(seconds=30)
    async def listing_sender(self):
        
        for each_file in self.get_all_file_names(folder_path="./database/items_list"):
            try:
                with open(f"database/items_list/{each_file}" , "r") as file:
                    data: list = json.load(file)

                one_item = data.pop(0)
                user_id = eval(each_file.replace(".json" , ""))

                user: discord.User = await self.bot.fetch_user(user_id)

                embed = discord.Embed(title=user.name , description="" , color=discord.Color.green())
                embed.add_field(name="Title" , value=one_item["title"] , inline=False)
                embed.add_field(name="Price" , value=f"{one_item['total_item_price']['amount']} {one_item['total_item_price']['currency_code']}" , inline=False)
                embed.add_field(name="Brand" , value=one_item["brand_title"] , inline=False)
                embed.add_field(name="Size" , value=one_item["size_title"] , inline=False)
                embed.add_field(name="Status" , value=one_item["status"] , inline=False)
                embed.add_field(name="Buy" , value=f"[Link]({one_item['url']})" , inline=False)
                embed.set_image(url=one_item["photo"]["url"])

                await user.send(embed=embed)

                with open(f"database/items_list/{each_file}" , "w") as file:
                    json.dump(data , file , indent=4)
            except Exception as e:
                print(e)

    @app_commands.command(name='start-tracking')
    async def start_tracking(self, interaction: discord.Interaction):
        await interaction.response.defer()
        try:
            db = Database("database/vinted_db.db")

            user = db.check_n_get_user(id=interaction.user.id , name=interaction.user.name)

            if not user or user.filter_link == None:
                return await interaction.followup.send('You need to set your filter link first', ephemeral=True)
            
            vinted = Vinted()
            one_item = vinted.items.search(user.filter_link , nbrItems=1)
            nbrItems = one_item[0].total_entries

            all_items = vinted.items.search(user.filter_link , nbrItems=nbrItems , json=True)

            with open(f"./database/items_list/{interaction.user.id}.json" , "w") as file:
                json.dump(all_items , file , indent=4)

            return await interaction.followup.send('Tracking started', ephemeral=True)
        except Exception as e:
            return await interaction.followup.send('Error starting tracking', ephemeral=True)

    @app_commands.command(name='set-filters')
    async def set_filters(self, interaction: discord.Interaction):
        """Opens a modal to set the filter link."""

        modal = FilterModal()
        await interaction.response.send_modal(modal)
        

async def setup(bot):
    await bot.add_cog(Tracker(bot))