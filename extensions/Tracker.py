import discord
from discord.ext import commands
from discord.ui import Modal, InputText
from methods.database import Database

class FilterModal(Modal):
    def __init__(self):
        super().__init__(title="Set Filter Link")
        self.filter_link = InputText(label="Filter Link", placeholder="Enter your filter link here", required=True)
        self.add_item(self.filter_link)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        filter_link = self.filter_link.value
        
        db = Database('vinted_db.db')
        db.insert_user(interaction.user.name, filter_link)

        await interaction.response.send_message(f'Filter link set to: {filter_link}', ephemeral=True)

class Tracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = Database('vinted_db.db')
        self.database.check_n_create_tables()

    @commands.command(name='set-filters')
    async def set_filters(self, ctx):
        """Opens a modal to set the filter link."""
        modal = FilterModal()
        await ctx.send_modal(modal)

async def setup(bot):
    await bot.add_cog(Tracker(bot))