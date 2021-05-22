"""testes para a classe BotQuest"""
import unittest
import asyncio
from unittest.mock import patch, MagicMock
from botquest.core import BotQuest


async def async_mock():
    """MagicMock precisa desse incentivo pra rodar métodos async:"""
    return 'meep!'

MagicMock.__await__ = lambda x: async_mock().__await__()


class TestBotQuest(unittest.TestCase):
    """classe principal de testes"""
    def setUp(self):
        """configura o ambiente de testes"""
        with patch('botquest.core.DBManager'):
            self.bot = BotQuest()

    def test_init(self):
        """testa inicialização do bot"""
        self.assertIs(type(self.bot), BotQuest)
        self.assertIs(type(self.bot.reactions), list)
        self.assertTrue(len(self.bot.reactions) > 0)
        for reaction in self.bot.reactions:
            self.assertTrue(
                hasattr(reaction, 'reaction') and callable(getattr(reaction, 'reaction'))
            )
        calls = self.bot.db.mock_calls
        self.assertTrue(len(calls) > 0, msg='db initialized')
        self.assertRegex(
            calls[0][1][0],
            '^CREATE TABLE IF NOT EXISTS reaction',
            msg='first db call always creates "reaction"'
        )
        for call in calls:
            self.assertIs(call[0], 'query', msg='only query() was called')
            self.assertRegex(
                call[1][0],
                '^CREATE TABLE IF NOT EXISTS ',
                msg='table only created if non-existant'
            )

    def test_load_reaction_error(self):
        """testa tratamento de erro ao carregar reaction"""
        with patch('logging.error') as mock, \
             patch('botquest.core.importlib.import_module', side_effect=ImportError('test')):
            res = self.bot.load_reaction('test_reaction')
            self.assertIsNone(res, msg='unable to load flawed reaction')
            mock.assert_called_once_with(
                'Failed to load reaction "test_reaction" (ImportError): test'
            )

    def test_on_message_same_author(self):
        """testa que o bot ignora mensagens de si próprio"""
        reaction = MagicMock()
        self.bot.active_reactions = MagicMock(return_value=[reaction])
        message = MagicMock()
        message.author = None
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.bot.on_message(message))
        loop.run_until_complete(task)
        message.assert_not_called()

    def test_on_message_other_author(self):
        """testa que o bot processa mensagens do discord"""
        reaction = MagicMock()
        self.bot.active_reactions = MagicMock(return_value=[reaction])
        message = MagicMock()
        message.author = 'someoneelse'
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.bot.on_message(message))
        loop.run_until_complete(task)
        self.bot.active_reactions.assert_called_once_with(message.guild.id)
        reaction.reaction.assert_called_once_with(message)

    def test_active_reactions(self):
        """testa lista de reações ativas"""
        self.bot.reactions = (MagicMock(), MagicMock(),)
        self.bot.db.query.return_value = [
            {'name': self.bot.reactions[0].name}, {'name': -1}, {'name': -2}
        ]
        res = self.bot.active_reactions(123)
        self.assertEqual(len(res), 1, msg='got active reaction')
        self.assertEqual(
            res[0].name,
            self.bot.reactions[0].name,
            msg='proper active reaction returned'
        )

    def test_on_guild_join(self):
        """testa tratamento do evento on_guild_join do discord"""
        self.bot.reactions = [MagicMock(), MagicMock()]
        with patch('logging.info') as mock:
            guild = MagicMock()
            guild.name = 'testguild'
            guild.id = '1234'
            guild.owner.name = 'testowner'
            loop = asyncio.get_event_loop()
            task1 = loop.create_task(self.bot.on_guild_join(guild))
            loop.run_until_complete(task1)
            mock.assert_called_once_with('joined guild "testguild" [1234] (created by testowner)')
            for r in self.bot.reactions:
                r.initialize_db.assert_called_once_with(guild.id)

    def test_on_ready(self):
        """testa tratamento do evento on_ready do discord"""
        with patch('logging.info') as mock:
            loop = asyncio.get_event_loop()
            task1 = loop.create_task(self.bot.on_ready())
            loop.run_until_complete(task1)
            mock.assert_called_once_with('connected as None')


if __name__ == '__main__':
    unittest.main()
