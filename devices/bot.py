"""
Main class for the bot
16/12/2023
Inès El Hadri
elhadrines@gmail.com
"""

# imports
from discord.ext import tasks
import discord
import json
import time


class Bot(discord.Client):
    """
    Les messages que le bot envoie dans le channel
    """

    def __init__(self, *args, **kwargs):
        discord.Client.__init__(self, *args, **kwargs)
        self.counter = 0

        self.load_events()

    def load_events(self):
        """load the dict of all events stored"""
        with open('events.json', 'r') as file:
            eventsstr = file.read()
        self.events = json.loads(eventsstr)

    def save_events(self):
        """saves the events in the file events.json"""
        with open('events.json', 'w') as file:
            file.write(json.dumps(self.events))

    def event_superpose(self, debut1, debut2, fin1, fin2):
        """si deux events se superposent"""
        if debut1 <= debut2 < fin1:
            return True
        if debut2 <= debut1 < fin2:
            return True
        return False

    def events_superpose(self, debut2, fin2):
        """si un event se superpose à ceux du dictionnaire"""
        for i, (k, v) in enumerate(self.events.items()):
            if self.event_superpose(v['debut'], debut2, v['fin'], fin2):
                return True
        return False

    async def on_ready(self):
        """when the bot is ready"""
        print(f'Logged in as {self.user} (ID: {self.user.id})')

    async def on_message(self, message):
        """stores the reservation"""
        if message.author == self.user:
            return

        # pour la réservation :
        if message.content.startswith('$reserve'):
            try:
                assert message.content[8] == ' '  # un espace apres $reserve
                plage = message.content[9:].split(' ')  # recuperer les plages horaires

                heure_debut = time.mktime(time.strptime(plage[0] + ' ' + plage[1], "%d/%m/%Y %H:%M"))
                heure_fin = time.mktime(time.strptime(plage[0] + ' ' + plage[2], "%d/%m/%Y %H:%M"))
                assert heure_debut < heure_fin

            except:
                await message.channel.send("Le format de réservation est : `$reserve JJ/MM/AAAA hh:mm hh:mm`")
                return

            if self.events_superpose(heure_debut, heure_fin):
                await message.channel.send("La date superpose une autre date.")
                return

            self.events[message.author.name] = {}
            self.events[message.author.name]['id'] = message.author.id
            self.events[message.author.name]['debut'] = heure_debut
            self.events[message.author.name]['fin'] = heure_fin
            self.events[message.author.name]['rappel'] = False
            self.save_events()
            await message.channel.send(time.strftime("Succès. Vous avez réservé le %d/%m/%Y de %H:%M",
                                                     time.localtime(heure_debut)) +
                                       time.strftime(" à %H:%M.",
                                                     time.localtime(heure_fin)))


        # pour supprimer sa réservation
        if message.content.startswith('$delete'):
            del self.events[message.author.name]
            self.save_events()
            await message.channel.send("Succès.")

    async def setup_hook(self) -> None:
        self.tache_arrplan.start()

    @tasks.loop(seconds=60)
    async def tache_arrplan(self):
        """envoie un mp 10min avant qu'une réservation ait lieu"""
        for i, (k, v) in enumerate(self.events.items()):
            user = await self.fetch_user(v['id'])
            if v['debut'] - time.time() < 600 and not v['rappel']:
                await user.send(f"<@{v['id']}>, tu as réservé ta salle pour dans 10min")
                self.events[user.name]['rappel'] = True
                self.save_events()

    @tache_arrplan.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()
