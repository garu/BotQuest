"""defina suas áreas de interesse no desenvolvimento de games:

!interesse game design            --> atribui interesse a quem pediu
!interesse -game design           --> remove interesse de quem pediu
!interesse                        --> lista todos os interesses disponíveis
!interesse create systems design  --> cria interesse (só admins)
!interesse remove systems design  --> remove interesse (só admins)
"""
import re
import logging
import discord
from botquest.reactionbase import ReactionBase


def _manages_roles(author):
    authorized = ['Questers', 'Moderador']
    ret = not {str(r) for r in author.roles}.isdisjoint(authorized)
    return ret


class Reaction(ReactionBase):
    """classe de reação para quando alguém manipular interesses"""
    def __init__(self, name, bot):
        self.actions = {
            'create': self._maybe_create_role,
            'remove': self._maybe_remove_role,
            'assign': self._maybe_assign_role,
            'unassign': self._maybe_unassign_role,
            'list': self._list_roles,
        }
        super().__init__(name, bot)

    def setup(self):
        """configura tabela usada como referência pela reaction"""
        self.bot.db.query(
            ('CREATE TABLE IF NOT EXISTS interesse ('
                'guild_id INTEGER,'
                'name TEXT,'
                'UNIQUE(guild_id,name))'),
            commit=True
        )

    async def reaction(self, msg):
        """reage quando mensagem é válida"""
        action, interest = self._parse_message(msg.content)
        if action is None:
            return None
        return await self.actions[action](msg, interest)

    def _parse_message(self, content):
        found = re.match(r'\s*!interesse\s*([^@]*)$', content)
        if not found:
            return None, None
        action, *options = re.split(r'\s+', found.group(1).rstrip())
        if not action:
            action = 'list'
            options = []
        elif action not in self.actions:
            if action[0] == '-':
                options.insert(0, action[1:])
                action = 'unassign'
            else:
                options.insert(0, action)
                action = 'assign'

        return action, ' '.join(options)

    async def _list_roles(self, msg, *_):
        roles = self._roles_from_db(msg.guild.id)
        reply = ', '.join(roles) if roles else 'Nenhum interesse configurado <o>'
        await msg.channel.send(reply)

    async def _maybe_create_role(self, msg, role_name):
        author = msg.author
        guild = author.guild
        if not _manages_roles(author):
            logging.warning(f'{author.name} tentou criar "{role_name}" em {guild.name}/{guild.id}')
            return None

        if self._get_role_from_name(msg, role_name):
            logging.warning(f'{author.name} tentou criar interesse preexistente "{role_name}" em {guild.name}/{guild.id}')
            return None

        try:
            await guild.create_role(name=role_name, reason='interesse criado por ' + author.name)
            self.bot.db.query(
                'INSERT INTO interesse (guild_id, name) VALUES (?, ?)',
                args=(guild.id, role_name,),
                commit=True
            )
            await msg.add_reaction("\U0001F44C")
        except discord.HTTPException as error:
            logging.error(f'erro criando interesse: {error} {author.name}/{role_name} ({type(error)})')
        return None

    async def _maybe_remove_role(self, msg, role_name):
        author = msg.author
        guild = author.guild
        if not _manages_roles(author):
            logging.warning(f'{author.name} tentou remover "{role_name}" em {guild.name}/{guild.id}')
            return None

        if role := self._get_role_from_name(msg, role_name):
            try:
                await role.delete()
                self.bot.db.query(
                    'DELETE FROM interesse WHERE guild_id=? AND name=?',
                    args=(guild.id, role_name,),
                    commit=True
                )
                await msg.add_reaction("\U0001F44C")
            except discord.HTTPException as error:
                logging.error(f'erro removendo interesse: {error} {author.name}/{role_name} ({type(error)})')
        else:
            logging.warning(f'{author.name} tentou remover interesse inexistente "{role_name}" em {guild.name}/{guild.id}')
        return None

    def _get_role_from_name(self, msg, role_name):
        author = msg.author
        guild = author.guild

        role = next((r for r in guild.roles if str(r) == role_name), None)
        if role is None or str(role) not in self._roles_from_db(guild.id):
            return None
        return role

    async def _maybe_assign_role(self, msg, role_name):
        if role_to_assign := self._get_role_from_name(msg, role_name):
            await msg.author.add_roles(role_to_assign, reason="dado pelo bot a pedido de @" + msg.author.name)
            await msg.add_reaction("\U0001F44C")
        return None

    async def _maybe_unassign_role(self, msg, role_name):
        if role_to_drop := self._get_role_from_name(msg, role_name):
            await msg.author.remove_roles(role_to_drop, reason="removido pelo bot a pedido de @" + msg.author.name)
            await msg.add_reaction("\U0001F44C")
        return None

    def _roles_from_db(self, guild_id):
        rows = self.bot.db.query(
            'SELECT name FROM interesse WHERE guild_id=?',
            args=(guild_id,)
        )
        return [row['name'] for row in rows] if rows else []
