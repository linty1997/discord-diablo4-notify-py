import discord


class InviteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        button = discord.ui.Button(label="Add bot to server",
                                   url="https://discord.com/api/oauth2/authorize?client_id=1114987226057670716&permissions=2147814464&scope=applications.commands%20bot",
                                   style=discord.ButtonStyle.link,
                                   emoji="👉")
        self.add_item(button)


