"""esse módulo define o BotQuest em si"""
import os
import sys
import re
import importlib
import asyncio
import logging
import discord


class BotQuest(discord.Client):
    """Classe principal do bot. Carrega plugins de reações e os chama
    conforme os eventos do discord vão acontecendo"""
    async def on_ready(self):
        """chamada sempre que o bot termina de se conectar ao Discord"""
        logging.info(f'connected as {self.user}')

    async def on_guild_join(self, guild):
        """chamada quando o bot entra numa nova guilda"""
        logging.info(f'joined guild "{guild.name}" [{guild.id}] (created by {guild.owner.name})')

    async def on_message(self, message):
        """chamada sempre que alguém enviar uma mensagem em algum canal que participamos"""
        # seria um pouco egocêntrico responder a si próprio :)
        if message.author == self.user:
            return
        await message.channel.send("Alô, mundo")
