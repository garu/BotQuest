"""esse módulo define o BotQuest em si"""
import os
import sys
import re
import importlib
import asyncio
import logging
import discord
from botquest.db_manager import DBManager


class BotQuest(discord.Client):
    """Classe principal do bot. Carrega plugins de reações e os chama
    conforme os eventos do discord vão acontecendo"""
    def __init__(self):
        self.reaction_dir = 'reactions'
        self.reactions = ()
        self.db = DBManager(os.path.join(
            os.path.dirname(__file__), '..', 'data', 'botquest.db'
        ))
        self.setup_reactions_db()
        self.load_all_reactions()
        super().__init__()

    async def on_ready(self):
        """chamada sempre que o bot termina de se conectar ao Discord"""
        logging.info(f'connected as {self.user}')

    async def on_guild_join(self, guild):
        """chamada quando o bot entra numa nova guilda"""
        logging.info(f'joined guild "{guild.name}" [{guild.id}] (created by {guild.owner.name})')
        for reaction in self.reactions:
            reaction.initialize_db(guild.id)

    async def on_message(self, message):
        """chamada sempre que alguém enviar uma mensagem em algum canal que participamos"""
        # seria um pouco egocêntrico responder a si próprio :)
        if message.author == self.user:
            return
        reactions = (r.reaction(message) for r in self.active_reactions(message.guild.id))
        await asyncio.gather(*reactions)

    def active_reactions(self, guild_id):
        """retorna toads as reactions ativas nessa guilda"""
        active = [row['name'] for row in self.db.query(
            'SELECT name FROM reaction WHERE guild_id=? AND active=1',
            args=(guild_id,)
        )]
        return [r for r in self.reactions if r.name in active]

    def load_all_reactions(self):
        """carrega todas as reações encontradas na pasta /reactions"""
        base_path = os.path.join(os.path.dirname(__file__), 'reactions')
        sys.path.append(base_path)    # evita exception de ModuleNotFound
        files = os.listdir(base_path)
        importlib.import_module('botquest.reactions')
        valids = []
        for file in files:
            if os.path.isfile(os.path.join(base_path, file)):
                regexp_result = re.search(r'(.+)\.py$', file)
                if regexp_result:
                    reaction_name = regexp_result.groups()[0]
                    reaction = self.load_reaction(reaction_name)
                    if reaction is not None:
                        valids.append(reaction)
        self.reactions = valids

    def load_reaction(self, reaction_name):
        """carrega uma reaction da pasta /reactions"""
        try:
            reaction_lib = importlib.import_module(
                reaction_name,
                package='botquest.reactions'
            )
            reaction = reaction_lib.Reaction(reaction_name, self)
            logging.info(f'reaction "{reaction_name}"" loaded')
            return reaction
        except (ImportError, AttributeError) as error:
            logging.error(f'Failed to load reaction "{reaction_name}"'
                          f' ({error.__class__.__name__}): {error}')
            return None

    def setup_reactions_db(self):
        """inicializa banco de dados, se necessário"""
        self.db.query(
            ('CREATE TABLE IF NOT EXISTS reaction ('
                'guild_id INTEGER NOT NULL,'
                'name TEXT NOT NULL,'
                'active INTEGER DEFAULT 1,'
                'UNIQUE (guild_id, name))'),
            commit=True
        )
