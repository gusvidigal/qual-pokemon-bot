from telebot.async_telebot import AsyncTeleBot
from mysql.connector import connect

token = "7751083686:AAEttmnu9AnqKKPRB6Qx9heUVghrvqJYuc8"
bot = AsyncTeleBot(token)

class BD():
    def __init__(self):
        self.partidas = {}

sql = connect(
  host="localhost",
  user="root",
  password="maisqlM41SQL",
  database="quemeessepokemon"
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