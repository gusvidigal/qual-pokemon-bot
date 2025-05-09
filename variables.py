from telebot.async_telebot import AsyncTeleBot
from mysql.connector import connect

token = "TOKEN"
bot = AsyncTeleBot(token)

class BD():
    def __init__(self):
        self.partidas = {}

sql = connect(
  host="localhost",
  user="---",
  password="---",
  database="---"
)
#PLACAR:
#nome varchar200 nn
#id varchar15 nn
#pontos int nn
#JOGANDO:
#id varchar20 nn
#CADASTRADOS:
#id varchar20 nn

bd = BD()
