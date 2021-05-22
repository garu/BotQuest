"""testes para a classe DBManager"""
import unittest
import sqlite3
from unittest.mock import patch
from botquest.db_manager import DBManager


class TestDBManager(unittest.TestCase):
    """classe principal de testes"""

    def test_database(self):
        """testa API e persistência de dados"""
        db_conn = DBManager(':memory:')
        self.assertEqual(db_conn.path, ':memory:')
        conn = db_conn.connect()
        self.assertIs(type(conn), sqlite3.Connection)
        # garante mesma conexão com o banco em todos os testes
        with patch.object(DBManager, 'connect', lambda x: conn):
            db = DBManager(':memory:')
            db.query(
                'CREATE TABLE test (name TEXT)',
                commit=True
            )
            db.query(
                'INSERT INTO test (name) values (?), (?)',
                args=('one', 'two'),
                commit=True
            )
            res = db.query('SELECT * FROM test ORDER BY name')
            self.assertEqual(len(res), 2)
            self.assertEqual(res[0]['name'], 'one')
            self.assertEqual(res[1]['name'], 'two')
            single = db.query(
                'SELECT * FROM test ORDER BY name',
                one=True
            )
            self.assertIs(type(single), sqlite3.Row)
            self.assertEqual(single['name'], 'one')


if __name__ == '__main__':
    unittest.main()
