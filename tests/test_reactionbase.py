"""testes para a classe ReactionBase"""
import unittest
from unittest.mock import Mock
from botquest.reactionbase import ReactionBase


class TestReactionBase(unittest.TestCase):
    """classe principal de testes"""
    def test_table_initialization(self):
        """testa inicialização de tabela de ativação"""
        bot = Mock()
        reaction = ReactionBase('base_test', bot)
        self.assertIsNotNone(reaction)
        reaction.initialize_db(123)
        bot.db.query.assert_called_once_with(
            'INSERT OR IGNORE INTO reaction (name, guild_id, active) VALUES (?, ?, 1)',
            args=('base_test', 123,),
            commit=True,
        )


if __name__ == '__main__':
    unittest.main()
