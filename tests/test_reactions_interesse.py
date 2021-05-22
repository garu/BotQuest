"""testes da reaction 'interesse'"""
import unittest
import asyncio
from unittest.mock import MagicMock, patch
import discord
from botquest.reactions import interesse


class TestInteresse(unittest.TestCase):
    """classe principal de testes"""
    def setUp(self):
        """configura objetos reutilizáveis"""
        self.msg = MagicMock(content='')
        self.bot = MagicMock()
        self.reaction = interesse.Reaction('interesse_test', self.bot)

    def _run_test(self):
        loop = asyncio.get_event_loop()
        task = loop.create_task(self.reaction.reaction(self.msg))
        res = loop.run_until_complete(task)
        return res

    def test_reaction_setup(self):
        """testa se a reaction inicia corretamente"""
        self.assertIs(type(self.reaction), interesse.Reaction)
        self.bot.db.query.assert_called_once()
        calls = self.bot.db.query.mock_calls
        self.assertRegex(
            calls[0][1][0],
            '^CREATE TABLE IF NOT EXISTS interesse ',
            msg='table initialized'
        )

    def test_invalid_reaction(self):
        """testa que frases inválidas não são reconhecidas"""
        self.msg.content = 'tenho algum !interesse mas nada sério'
        self.bot.db.query.reset_mock()
        self._run_test()
        self.msg.channel.send.assert_not_called()
        self.msg.add_reaction.assert_not_called()
        self.bot.db.query.assert_not_called()

    def test_reaction_list_is_empty(self):
        """testa listagem quando não há itens"""
        self.msg.content = '!interesse'
        self.bot.db.query.reset_mock()
        self.bot.db.query.return_value = None
        self._run_test()
        self.msg.add_reaction.assert_not_called()
        self.msg.channel.send.assert_called_once_with('Nenhum interesse configurado <o>')

    def test_reaction_list_has_items(self):
        """testa listagem quando há itens"""
        self.msg.content = '!interesse'
        self.bot.db.query.reset_mock()
        self.bot.db.query.return_value = [{'name': 'role1'}, {'name': 'role2'}]
        self._run_test()
        self.msg.add_reaction.assert_not_called()
        self.msg.channel.send.assert_called_once_with('role1, role2')
        self.bot.db.query.assert_called_once()

    def test_reaction_create_with_bad_user(self):
        """testa criação quando usuário não pode criar"""
        self._reaction_management_test_bad_user('create', 'criar')

    def test_reaction_create_existing_role(self):
        """testa criação quando interesse já está criado"""
        self.msg.content = '!interesse create um interesse legal'
        self.bot.db.query.reset_mock()
        self.bot.db.query.return_value = [{'name': 'um interesse legal'}]
        self.msg.author.name = 'Jane Test'
        self.msg.author.guild.name = 'Jacaranda'
        self.msg.author.guild.roles = ['um interesse legal']
        self.msg.author.roles = ['Moderador', 'Bar']
        with patch('botquest.reactions.interesse.logging') as mock:
            self._run_test()
            mock.warning.assert_called_once_with(
                ('Jane Test tentou criar interesse preexistente "um interesse legal" '
                 f'em {self.msg.author.guild.name}/{self.msg.author.guild.id}')
            )
            self.msg.add_reaction.assert_not_called()
            self.msg.channel.send.assert_not_called()
            self.bot.db.query.assert_called_once()

    def test_reaction_create_role_discord_error(self):
        """testa criação quando discord dá erro"""
        self.msg.content = '!interesse create alguma coisa'
        self.bot.db.query.reset_mock()
        self.bot.db.query.return_value = []
        self.msg.author.name = 'Jane Test'
        self.msg.author.guild.name = 'Jacaranda'
        self.msg.author.guild.roles = ['alguma coisa']
        self.msg.author.guild.create_role.side_effect = discord.HTTPException(
            response=MagicMock(),
            message='guild boom'
        )
        self.msg.author.roles = ['Moderador', 'Bar']
        with patch('botquest.reactions.interesse.logging') as mock:
            self._run_test()
            calls = mock.error.mock_calls
            self.assertEqual(len(calls), 1, 'single error')
            self.assertRegex(calls[0][1][0], '^erro criando interesse: ')
            self.msg.add_reaction.assert_not_called()
            self.msg.channel.send.assert_not_called()
            self.bot.db.query.assert_called_once()

    def test_reaction_create_role_ok(self):
        """testa criação sem incidentes"""
        self.msg.content = '!interesse create alguma coisa'
        self.bot.db.query.reset_mock()
        self.bot.db.query.return_value = []
        self.msg.author.name = 'Jane Test'
        self.msg.author.guild.name = 'Jacaranda'
        self.msg.author.guild.roles = ['alguma coisa']
        self.msg.author.roles = ['Moderador', 'Bar']
        self._run_test()
        self.msg.add_reaction.assert_called_once_with('👌')
        self.msg.channel.send.assert_not_called()
        calls = self.bot.db.query.mock_calls
        self.assertEqual(len(calls), 2, msg='database called 2 times')
        self.assertRegex(calls[0][1][0], '^SELECT ', msg='first we search')
        self.assertRegex(calls[1][1][0], '^INSERT INTO ', msg='then we add')

    def test_reaction_remove_with_bad_user(self):
        """testa remoção quando usuário não pode criar"""
        self._reaction_management_test_bad_user('remove', 'remover')

    def _reaction_management_test_bad_user(self, action, message_log):
        """método auxiliar para testar criação/remoção de interesses"""
        self.msg.content = f'!interesse {action} um interesse legal'
        self.bot.db.query.reset_mock()
        self.msg.author.name = 'Jane Test'
        self.msg.author.guild.name = 'Jacaranda'
        self.msg.author.roles = ['Foo', 'Bar']
        with patch('botquest.reactions.interesse.logging') as mock:
            self._run_test()
            self.msg.add_reaction.assert_not_called()
            self.msg.channel.send.assert_not_called()
            self.bot.db.query.assert_not_called()
            mock.warning.assert_called_once_with(
                (f'Jane Test tentou {message_log} "um interesse legal" '
                 f'em {self.msg.author.guild.name}/{self.msg.author.guild.id}')
            )

    def test_reaction_remove_non_existing_role(self):
        """testa remoção de interesse que não existe"""
        self.msg.content = '!interesse remove um interesse legal'
        self.bot.db.query.reset_mock()
        self.bot.db.query.return_value = [{'name': 'outra coisa'}]
        self.msg.author.name = 'Jane Test'
        self.msg.author.guild.name = 'Jacaranda'
        self.msg.author.guild.roles = ['outra coisa']
        self.msg.author.roles = ['Moderador', 'Bar']
        with patch('botquest.reactions.interesse.logging') as mock:
            self._run_test()
            mock.warning.assert_called_once_with(
                ('Jane Test tentou remover interesse inexistente "um interesse legal" '
                 f'em {self.msg.author.guild.name}/{self.msg.author.guild.id}')
            )
            self.msg.add_reaction.assert_not_called()
            self.msg.channel.send.assert_not_called()
            self.bot.db.query.assert_not_called()

    def test_reaction_remove_role_discord_error(self):
        """testa remoção quando discord dá erro"""
        role_str = 'alguma coisa'
        self.msg.content = f'!interesse remove {role_str}'
        self.bot.db.query.reset_mock()
        self.bot.db.query.return_value = [{'name': role_str}]
        self.msg.author.name = 'Jane Test'
        self.msg.author.guild.name = 'Jacaranda'
        role_mock = MagicMock()
        role_mock.name = role_str
        role_mock.__str__.return_value = role_str
        role_mock.delete.side_effect = discord.HTTPException(
            response=MagicMock(),
            message='guild boom'
        )
        self.msg.author.guild.roles = [role_mock]
        self.msg.author.roles = ['Moderador', 'Bar']
        with patch('botquest.reactions.interesse.logging') as mock:
            self._run_test()
            calls = mock.error.mock_calls
            self.assertEqual(len(calls), 1, 'single error')
            self.assertRegex(calls[0][1][0], '^erro removendo interesse: ')
            self.msg.add_reaction.assert_not_called()
            self.msg.channel.send.assert_not_called()
            self.bot.db.query.assert_called_once()

    def test_reaction_remove_role_ok(self):
        """testa remoção sem incidentes"""
        role_str = 'alguma coisa'
        self.msg.content = f'!interesse remove {role_str}'
        self.bot.db.query.reset_mock()
        self.bot.db.query.return_value = [{'name': role_str}]
        self.msg.author.name = 'Jane Test'
        self.msg.author.guild.name = 'Jacaranda'
        role_mock = MagicMock()
        role_mock.name = role_str
        role_mock.__str__.return_value = role_str
        self.msg.author.guild.roles = [role_mock]
        self.msg.author.roles = ['Moderador', 'Bar']
        self._run_test()
        self.msg.add_reaction.assert_called_once_with('👌')
        self.msg.channel.send.assert_not_called()
        calls = self.bot.db.query.mock_calls
        self.assertEqual(len(calls), 2, msg='database called 2 times')
        self.assertRegex(calls[0][1][0], '^SELECT ', msg='first we search')
        self.assertRegex(calls[1][1][0], '^DELETE FROM ', msg='then we add')

    def test_reaction_assign_role_ok(self):
        """testa atribuição sem incidentes"""
        self.msg.content = '!interesse alguma coisa'
        self.bot.db.query.reset_mock()
        self.bot.db.query.return_value = [{'name': 'alguma coisa'}]
        self.msg.author.name = 'Jane Test'
        self.msg.author.guild.name = 'Jacaranda'
        self.msg.author.guild.roles = ['alguma coisa']
        self.msg.author.roles = []
        self._run_test()
        self.msg.author.add_roles.assert_called_once_with(
            'alguma coisa', reason='dado pelo bot a pedido de @Jane Test'
        )
        self.msg.add_reaction.assert_called_once_with('👌')
        self.msg.channel.send.assert_not_called()
        calls = self.bot.db.query.mock_calls
        self.assertEqual(len(calls), 1, msg='database called 1 times')
        self.assertRegex(calls[0][1][0], '^SELECT ', msg='simple search')

    def test_reaction_assign_role_not_found(self):
        """testa atribuição quando interesse não existe"""
        self.msg.content = '!interesse alguma coisa'
        self.bot.db.query.reset_mock()
        self.bot.db.query.return_value = []
        self.msg.author.name = 'Jane Test'
        self.msg.author.guild.name = 'Jacaranda'
        self.msg.author.guild.roles = ['alguma coisa']
        self.msg.author.roles = []
        self._run_test()
        self.msg.add_reaction.assert_not_called()
        self.msg.channel.send.assert_not_called()
        calls = self.bot.db.query.mock_calls
        self.assertEqual(len(calls), 1, msg='database called 1 times')
        self.assertRegex(calls[0][1][0], '^SELECT ', msg='simple search')

    def test_reaction_unassign_role_ok(self):
        """testa desatribuição sem incidentes"""
        self.msg.content = '!interesse -alguma coisa'
        self.bot.db.query.reset_mock()
        self.bot.db.query.return_value = [{'name': 'alguma coisa'}]
        self.msg.author.name = 'Jane Test'
        self.msg.author.guild.name = 'Jacaranda'
        self.msg.author.guild.roles = ['alguma coisa']
        self.msg.author.roles = []
        self._run_test()
        self.msg.author.remove_roles.assert_called_once_with(
            'alguma coisa', reason='removido pelo bot a pedido de @Jane Test'
        )
        self.msg.add_reaction.assert_called_once_with('👌')
        self.msg.channel.send.assert_not_called()
        calls = self.bot.db.query.mock_calls
        self.assertEqual(len(calls), 1, msg='database called 1 times')
        self.assertRegex(calls[0][1][0], '^SELECT ', msg='simple search')

    def test_reaction_unassign_role_not_found(self):
        """testa desatribuição quando interesse não existe"""
        self.msg.content = '!interesse alguma coisa'
        self.bot.db.query.reset_mock()
        self.bot.db.query.return_value = []
        self.msg.author.name = 'Jane Test'
        self.msg.author.guild.name = 'Jacaranda'
        self.msg.author.guild.roles = ['alguma coisa']
        self.msg.author.roles = []
        self._run_test()
        self.msg.add_reaction.assert_not_called()
        self.msg.channel.send.assert_not_called()
        calls = self.bot.db.query.mock_calls
        self.assertEqual(len(calls), 1, msg='database called 1 times')
        self.assertRegex(calls[0][1][0], '^SELECT ', msg='simple search')


if __name__ == '__main__':
    unittest.main()
