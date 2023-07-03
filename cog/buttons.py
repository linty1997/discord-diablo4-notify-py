import discord


class InviteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        button = discord.ui.Button(label="Add bot to server",
                                   url="https://discord.com/api/oauth2/authorize?client_id=1114987226057670716&permissions=2147814464&scope=applications.commands%20bot",
                                   style=discord.ButtonStyle.link,
                                   emoji="👉")
        self.add_item(button)


class BindingLineNotifyView(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=None)
        button = discord.ui.Button(label="Binding Line Notify",
                                   url=f"https://notify-bot.line.me/oauth/authorize?response_type=code&scope=notify"
                                       f"&response_mode=form_post&client_id=tXER2MQIt1wfAZIOm3rZYV&redirect_uri=https"
                                       f"://d4-notify.glacat.com&state={user_id}",
                                   style=discord.ButtonStyle.link,
                                   emoji="✅")
        self.add_item(button)
