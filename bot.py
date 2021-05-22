"""script que executa o BotQuest"""
import os
import logging
from botquest.core import BotQuest

logging.basicConfig(level=logging.INFO)
bot = BotQuest()
bot.run(os.environ['BOTQUESTID'])
