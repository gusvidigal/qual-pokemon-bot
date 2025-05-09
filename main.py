import asyncio
import handlers

from telebot.types import ReactionTypeEmoji
from telebot import formatting

from pokes import pokemon_list
from functions import *
from variables import bot, bd, sql

#Limpa a tabela JOGANDO, uma vez que as partidas não são salvas quando o bot reinicia
cursor = sql.cursor()
cursor.execute("DELETE FROM JOGANDO")
sql.commit()
cursor.close()


#Comandos
bot.register_message_handler(handlers.placar, commands=['placar'])
bot.register_message_handler(handlers.cadastrar, commands=['cadastrar'])
bot.register_message_handler(handlers.descadastrar, commands=['descadastrar'])   
bot.register_message_handler(handlers.menuJogo, commands=['jogarpoke'])
bot.register_message_handler(handlers.adivinhar,
                             func=lambda msg: userId(msg) in getList("CADASTRADOS", "ID", True) and chatId(msg) in getList("JOGANDO", "ID", True),
                             chat_types=['private', 'group'])

bot.register_callback_query_handler(
    handlers.respostaMenuJogo_selecionando,
    func=lambda call: "nn" in call.data)
bot.register_callback_query_handler(
    handlers.respostaMenuJogo_gen,
    func=lambda call: "ss" in call.data)        
bot.register_callback_query_handler(
    handlers.respostaMenuJogo_modo,
    func=lambda call: call.data[:2] in ["or", "cr"])        
bot.register_callback_query_handler(
    handlers.respostaMenuJogo_tempo,
    func=lambda call: call.data[:2] in ["15", "30", "60"])

#Assim o bot não recebe trilhões de updates quando inicia
async def ignorarUpdates():
    updates = await bot.get_updates()
    if updates:
        await bot.get_updates(offset=updates[-1].update_id + 1)

asyncio.run(ignorarUpdates())
asyncio.run(bot.polling())
    

