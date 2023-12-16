"""
Main program for the bot
16/12/2023
Inès El Hadri
elhadrines@gmail.com
"""

import discord
import os
from dotenv import load_dotenv
from devices.bot import Bot

# pour le .env
load_dotenv()

# ?? jcp mais nécessaire
intents = discord.Intents.default()
intents.message_content = True
client = Bot(intents=intents)

# run bot
client.run(os.getenv('TOKEN'))
