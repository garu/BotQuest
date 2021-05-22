__version__ = '1.0'
"""rola dados com ou sem modificadores:
    !roll 2d6 +4
    !roll 1d20
"""
import re
import random
from botquest.reactionbase import ReactionBase


class Reaction(ReactionBase):
    """classe de reação para eventos de rolagem de dados"""

    async def reaction(self, msg):
        """reage quando mensagem é válida"""
        (how_many, max_num, sign, modifier) = self._parse_message(msg.content)

        dice = self._roll_dice(how_many, max_num)
        if dice is None:
            return None
        else:
            reply = self._format_for_print(dice, sign, modifier, max_num)
            await msg.channel.send(reply)

    def _parse_message(self, content):
        found = re.match(
            r'\s*!roll (\d)\s*[dD](\d{1,3})\s*(?:(\+|\-)\s*(\d{1,4}))?\s*$',
            content
        )
        if found:
            return [int(x) if x.isdigit() else x for x in found.groups('0')]
        return [0, 0, 0, 0]

    def _roll_dice(self, how_many, max_num):
        if how_many <= 0 or max_num <= 0:
            return None
        return [random.randint(1, max_num) for i in range(how_many)]

    def _sum(self, dice, sign, modifier):
        if sign == '-':
            modifier = -modifier
        return sum(dice, modifier)

    def _format_for_print(self, dice, sign, modifier, max_num):
        total = self._sum(dice, sign, modifier)
        return_msg = ' '.join([self._maybe_wrap(roll, max_num) for roll in dice])
        if modifier > 0:
            return_msg += f' {sign}{modifier}'
        return_msg += f' = **{total}**'
        return return_msg

    def _maybe_wrap(self, roll, max_num):
        if roll in [1, max_num]:
            return f'[**{roll}**]'
        else:
            return f'[{roll}]'
