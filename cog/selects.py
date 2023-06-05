import discord
from cog.modal import *


class ReportView(discord.ui.View):
    @discord.ui.select(
        placeholder="Choose a Event!",
        min_values=1,
        max_values=1,
        options=[
            discord.SelectOption(
                label="WordBoss",
                description="Reporting World Boss Spawn Time."
            ),
        ]
    )
    async def select_callback(self, select, interaction):
        await interaction.response.send_modal(WordBossModal(title="WordBossFrom"))
