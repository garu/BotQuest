"""define a base para reactions, com atributos e métodos comuns."""


class ReactionBase():
    """toda reaction deve estender essa classe"""
    def __init__(self, name, bot):
        self.name = name
        self.bot = bot
        self.setup()

    def initialize_db(self, guild_id):
        """inicializa reaction ao entrar numa nova guilda"""
        self.bot.db.query(
            'INSERT OR IGNORE INTO reaction (name, guild_id, active) VALUES (?, ?, 1)',
            args=(self.name, guild_id),
            commit=True
        )

    def setup(self):
        """inicializa valores da reaction, se necessário. Implementada pelas subclasses"""
