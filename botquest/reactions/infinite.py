__version__ = '1.0'
"""contador de dias sem falar da maior obra prima dos videogames"""

import re
from datetime import datetime as dt
from botquest.reactionbase import ReactionBase


class Reaction(ReactionBase):
    """classe de reação para quando alguém citar Bioshock Infinite"""

    def setup(self):
        """configura tabela usada como referência pela reaction"""
        self.bot.db.query(
            ('CREATE TABLE IF NOT EXISTS infinite ('
                'guild_id INTEGER PRIMARY KEY,'
                'last_mention_date TEXT,'
                'record_days INTEGER, '
                'last_vocalization TEXT)'),
            commit=True
        )

    async def reaction(self, msg):
        """reage quando mensagem é válida"""
        found = re.search('infinite|:elizabeth:', msg.content, flags=re.IGNORECASE)
        if not found:
            return None

        entry = self._get_last_entry(msg.guild.id)
        entry['last_mention_date'] = dt.today()

        if entry['is_new_record']:
            entry['record_days'] = entry['delta_days']

        if entry['can_reply']:
            entry['last_vocalization'] = dt.today()

        query = self._build_update_query(msg.guild.id, entry)
        self.bot.db.query(query[0], args=query[1], commit=True)

        if entry['can_reply']:
            reply = self._build_reply_string(
                entry.get('record_days', entry['record_days'])
            )
            await msg.channel.send(reply)
        return None

    def _get_last_entry(self, guild_id):
        row = self.bot.db.query(
            ('SELECT guild_id,last_mention_date,record_days,last_vocalization '
                'FROM infinite WHERE guild_id=?'),
            args=(guild_id,),
            one=True
        )
        if row is None:
            row = {
                "guild_id": guild_id,
                "last_mention_date": str(dt.today()),
                "record_days": 0,
                "last_vocalization": '1970-01-01 00:00:00',
            }
        else:
            row = dict(row)

        row['delta_days'] = (dt.today() - dt.fromisoformat(row['last_mention_date'])).days
        row['is_new_record'] = row['delta_days'] > row['record_days']
        row['can_reply'] = (dt.today() - dt.fromisoformat(row['last_vocalization'])).total_seconds() > 60 * 60 * 3
        return row

    def _build_update_query(self, guild_id, data):
        query = ('INSERT INTO infinite ('
                 'guild_id, last_mention_date, record_days, last_vocalization) '
                 'VALUES (?,?,?,?) '
                 'ON CONFLICT (guild_id) DO '
                 'UPDATE SET last_mention_date=?, record_days=?, last_vocalization=? '
                 'WHERE guild_id=?')
        values = [
            data['guild_id'], data['last_mention_date'], data['record_days'], data['last_vocalization'],
            data['last_mention_date'], data['record_days'], data['last_vocalization'], data['guild_id'],
        ]
        return (query, values)

    def _build_reply_string(self, days):
        days_in_emoji = self._num2emoji(days)
        return (
            ('Estamos a :zero: dias sem falar de Bioshock Infinite. '
             f'Nosso recorde é de {days_in_emoji} dias. '
             ':construction: <:elizabeth:590739833811632149> :construction:')
        )

    def _num2emoji(self, num):
        emoji = ''

        num2literal = {
            '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
            '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'
        }
        for i in str(num):
            if i in num2literal:
                emoji += ':' + num2literal[i] + ':'
        return emoji
