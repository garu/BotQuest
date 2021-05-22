__version__ = '1.0'
"""escolha aleatoriamente entre opções.
simples => !escolha A ou B ou C (ou D ou E...)
com pesos => !escolha bioshock infinite^10 ou fallout 4 ou fifa^3
"""
import re
import random
from botquest.reactionbase import ReactionBase


class Reaction(ReactionBase):
    """classe de reação para eventos de escolha entre N opções"""

    async def reaction(self, msg):
        """reage quando mensagem é válida"""
        found = re.search(r'^!escolha\s+(.+)$', msg.content)
        if not found:
            return None
        options = re.split(r'\s+ou\s+', found.group(1))
        if len(options) <= 1:
            await msg.channel.send('Não encontrei as opções (separe com "ou")')
        else:
            weights = []
            domain = []
            for opt in options:
                found = re.search(r'^\s*(.+?)(?:\^(\d+))?\s*$', opt)
                filtered = found.group(1)
                weight = found.group(2) or 1
                weights.append(int(weight))
                domain.append(filtered)
            random.seed()
            pick = random.choices(population=domain, weights=weights, k=1)
            await msg.channel.send(pick[0])
