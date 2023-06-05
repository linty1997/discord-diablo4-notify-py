import discord
from cog.controller import WordBossController


class WordBossModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Appearance time", placeholder="use: MM-dd HH:mm e.g.: 06-04 01:00",
                                           min_length=11, max_length=11))
        self.add_item(discord.ui.InputText(label="Time zone", placeholder="use: UTC Time zone e.g.: UTC+0 input 0,"
                                                                          " UTC+12 input 12",
                                           min_length=1, max_length=2))

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(invisible=True)
        appearance_time = self.children[0].value
        time_zone = self.children[1].value
        res = await WordBossController(interaction).update(appearance_time, time_zone)
        embed_colour = discord.Colour.green() if res else discord.Colour.red()
        embed_description = "Done." if res else "Failed."
        embed = discord.Embed(title="WordBossFrom", description=embed_description, colour=embed_colour)
        embed.add_field(name="Appearance time", value=appearance_time)
        embed.add_field(name="Time zone", value=time_zone)
        embed.set_footer(text="Please refrain from malicious submissions. Malicious submissions will result in a "
                              "permanent ban.")

        await interaction.followup.send(embeds=[embed], ephemeral=True)
