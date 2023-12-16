"""
Main class for the bot
16/12/2023
Inès El Hadri
elhadrines@gmail.com
"""

# imports
from discord.ext import tasks
import discord


class Bot(discord.Client):
    """
    Les messages que le bot envoie dans le channel
    """
    def __init__(self, *args, **kwargs):
        discord.Client.__init__(self, *args, **kwargs)
        self.counter = 0

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content.startswith('$hello'):
            await message.channel.send('Hello!')

    async def setup_hook(self) -> None:
        self.tache_arrplan.start()

    @tasks.loop(seconds=60)
    async def tache_arrplan(self):
        channel = self.get_channel(1185600265882173472)
        self.counter += 1
        await channel.send(str(self.counter))

    @tache_arrplan.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()
