"""manipula o banco de dados do BotQuest"""
import sqlite3


class DBManager():
    """Interface entre o programa e o banco de dados.
    É instanciada pelo bot automaticamente"""
    def __init__(self, path):
        self.path = path

    def connect(self):
        """retorna uma conexão ativa com o banco de dados"""
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def query(self, query, args=(), one=False, commit=False):
        """executa a query recebida e retorna seu resultado"""
        conn = self.connect()
        cur = conn.execute(query, args)
        if commit is True:
            conn.commit()
        ret = cur.fetchall()
        cur.close()
        return (ret[0] if ret else None) if one else ret
