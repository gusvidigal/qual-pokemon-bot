from telebot.formatting import format_text, mbold, escape_markdown

from variables import bot, bd
from functions import *
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReactionTypeEmoji

import asyncio

#Comandos
async def placar(msg):
    
    resultados = getList("PLACAR", "NOME, ID, PONTOS")
    lista = []
    for i in resultados:
        lista.append({"nome": i[0], "id": i[1], "pontos": i[2]})
    texto_placar = gerarPlacar(lista)
    
    await bot.send_message(chat_id=msg.chat.id,parse_mode="MarkdownV2",
                           text=format_text(mbold("Placar geral:\n"),texto_placar, separator=""))
    
async def cadastrar(msg, jogando=False):
    if userId(msg) in getList("CADASTRADOS","ID", True):
        await bot.reply_to(msg, text=format_text("Você ", mbold("já está"), escape_markdown(" cadastrado!"), separator=""),parse_mode="MarkdownV2")
    else:
        addInTable("CADASTRADOS", (userId(msg),), "ID")
        addInTable("PLACAR", (msg.from_user.first_name, userId(msg), "0"), "NOME, ID, PONTOS")
        if chatId(msg) in getList("JOGANDO", "ID", True):
            flag = False
            for dic in bd.partidas[chatId(msg)].placar:
                if dic["id"] == userId(msg):
                    flag = True
            if not flag:
                bd.partidas[chatId(msg)].placar.append({"nome": msg.from_user.first_name, "id": userId(msg), "pontos": 0})
        if not jogando:
            await bot.reply_to(msg, text="Você foi cadastrado!")
        
async def descadastrar(msg):
    if userId(msg) not in getList("CADASTRADOS", "ID", True):
        await bot.reply_to(msg, text=format_text("Você ", mbold("não está"), escape_markdown(" cadastrado!"), separator=""),parse_mode="MarkdownV2")
    else:
        delInTable("CADASTRADOS", userId(msg), "ID")
        delInTable("PLACAR", userId(msg), "ID")
        await bot.reply_to(msg, text="Você foi descadastrado!")


#Ao usar /jogarpoke, os usuários caem nesse menu
async def menuJogo(msg):
    msg.text = msg.text.strip()
    if chatId(msg) in getList("JOGANDO", "ID", True):
        await bot.send_message(chat_id=msg.chat.id,parse_mode="MarkdownV2",
                               text=format_text(mbold("Já existe "),escape_markdown("um jogo em andamento neste chat!"),separator=""))
        return
    if userId(msg) not in getList("CADASTRADOS","ID",True):
        await cadastrar(msg, True)
        
    botoes = InlineKeyboardMarkup()
    botoes.row_width = 5
    botoes.row(InlineKeyboardButton("Próximo (todas)", callback_data="ss-g123456789"))
    botoes.row(InlineKeyboardButton("ger I", callback_data="nn-g1"),
                InlineKeyboardButton("ger II", callback_data="nn-g2"),
                InlineKeyboardButton("ger III", callback_data="nn-g3"),
                InlineKeyboardButton("ger IV", callback_data="nn-g4"))
    botoes.row(InlineKeyboardButton("ger V", callback_data="nn-g5"),
                InlineKeyboardButton("ger VI", callback_data="nn-g6"),
                InlineKeyboardButton("ger VII", callback_data="nn-g7"),
                InlineKeyboardButton("ger VIII", callback_data="nn-g8"),
                InlineKeyboardButton("ger IX", callback_data="nn-g9"))

    await bot.send_message(chat_id=msg.chat.id, parse_mode="MarkdownV2",
                           text=format_text(mbold("Quem é esse Pokémon?"),"\n\nPara jogar, ",mbold("selecione uma ou mais gerações abaixo."),separator=""),
                           reply_markup=botoes)
#O menu é atualizado a cada clique até clicar em "próximo"
async def respostaMenuJogo_selecionando(call):
    msg = call.message
    
    gens = list(call.data[4:])
    gen_formatadas = ", ".join(gens) if len(gens)!=0 and len(gens)!=9 else "todas"
    
    def toggle(gen):
        gen = str(gen)
        lista = gens.copy()
        if gen in lista:
            lista.remove(gen)
        else: lista.append(gen)
        lista.sort(key=lambda el: int(el))
        return "".join(lista)
    
    botoes = InlineKeyboardMarkup()
    botoes.row_width = 5
    botoes.row(InlineKeyboardButton("Próximo ({})".format(gen_formatadas), callback_data="ss-g"+("".join(gens) if len(gens)!=0 else "123456789")))
    botoes.row(InlineKeyboardButton("ger I", callback_data="nn-g"+toggle(1)),
                InlineKeyboardButton("ger II", callback_data="nn-g"+toggle(2)),
                InlineKeyboardButton("ger III", callback_data="nn-g"+toggle(3)),
                InlineKeyboardButton("ger IV", callback_data="nn-g"+toggle(4)))
    botoes.row(InlineKeyboardButton("ger V", callback_data="nn-g"+toggle(5)),
                InlineKeyboardButton("ger VI", callback_data="nn-g"+toggle(6)),
                InlineKeyboardButton("ger VII", callback_data="nn-g"+toggle(7)),
                InlineKeyboardButton("ger VIII", callback_data="nn-g"+toggle(8)),
                InlineKeyboardButton("ger IX", callback_data="nn-g"+toggle(9)))
    await bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.id,parse_mode="MarkdownV2",
                           text=format_text(mbold("Quem é esse Pokémon?"),
                                            "\n\nPara jogar, ",
                                            mbold("selecione uma ou mais gerações abaixo."),
                                            "\n\n",mbold("Gerações selecionadas: "),gen_formatadas,
                                            separator=""),
                           reply_markup=botoes)

#Menu de seleção do modo
async def respostaMenuJogo_gen(call):
    msg = call.message
    
    botoes = InlineKeyboardMarkup()
    botoes.row_width = 2
    botoes.row(InlineKeyboardButton("Original", callback_data="or-{}".format(call.data.replace("ss-", ""))),
               InlineKeyboardButton("Em cores", callback_data="cr-{}".format(call.data.replace("ss-", ""))))
    
    await bot.edit_message_text(chat_id=msg.chat.id, parse_mode="MarkdownV2", message_id=msg.id,
                                text=format_text("Agora, ",mbold("escolha um modo de jogo abaixo."),separator=""), reply_markup=botoes)

#Menu de seleção do tempo
async def respostaMenuJogo_modo(call):
    msg = call.message
    
    botoes = InlineKeyboardMarkup()
    botoes.row_width = 3
    botoes.row(InlineKeyboardButton("15s", callback_data="15-{}".format(call.data)),
               InlineKeyboardButton("30s", callback_data="30-{}".format(call.data)),
               InlineKeyboardButton("1min", callback_data="60-{}".format(call.data)))
    
    await bot.edit_message_text(chat_id=msg.chat.id, parse_mode="MarkdownV2", message_id=msg.id,
                                text=format_text("Por fim, ",mbold("escolha o tempo das respostas."),separator=""), reply_markup=botoes)

#Início do jogo
async def respostaMenuJogo_tempo(call):
    
    msg = call.message
    
    #tt-mm-gnnnnnnnnn"
    gen = list(call.data[7:])
    modo = "original" if call.data[3:5] == "or" else "em cores"
    tempo = int(call.data[:2])
    
    await bot.edit_message_text(chat_id=msg.chat.id,parse_mode="MarkdownV2", message_id=msg.id,
                                text=format_text("Jogo escolhido:\n",mbold("Gerações: "),
                                                 ("todas" if len(gen)==9 else ", ".join(gen)),mbold("\nModo: "),modo,
                                                 mbold("\nTempo: "),str(tempo)+"s",separator=""))
    await iniciarJogo(gen, modo, tempo, msg)
#Jogo
async def iniciarJogo(gen, modo, tempo, msg):
    
    if chatId(msg) in getList("JOGANDO", "ID", True):
        await bot.edit_message_text(chat_id=msg.chat.id,parse_mode="MarkdownV2", message_id=msg.id,
                                        text=format_text(mbold("Já existe "),escape_markdown("um jogo em andamento neste chat!"),separator=""))
        return
    
    gen = list(map(int,gen.copy()))
    addInTable("JOGANDO", (chatId(msg),) , "ID")
    bd.partidas[chatId(msg)] = Partida(chatId(msg), gen)
    part = bd.partidas[chatId(msg)]
    await bot.send_message(chat_id=msg.chat.id, parse_mode="MarkdownV2", text=format_text(mbold("Jogo iniciando...")))
    
    while True:
        part.escolherPoke()
        print(part.imagem)

        imagem = await processarImagem(part.imagem, modo)
        await bot.send_photo(chat_id=msg.chat.id, photo=imagem)
        
        
        asyncio.create_task(part.timeout(part.rodada, tempo))
        await part.promise.wait()
        
        part.promise.clear()
        
        part.rodada += 1
        if part.acertado == 'n': break
        
        await asyncio.sleep(0.5)
        
        texto_placar = gerarPlacar(part.placar)
        await bot.send_message(chat_id=msg.chat.id,parse_mode='MarkdownV2',
                               text=format_text(mbold("Placar:\n"), texto_placar, mbold("\nRodada: "), str(part.rodada), separator=""))

        #O processamento do modo "em cores" demora menos, por isso adicionar o tempo para compensar
        await asyncio.sleep(0.5 if modo == "original" else 2.5)
        part.acertado = ''
        
    delInTable("JOGANDO", part.chat, "ID")
    
    if modo == "original":
        imagem_perda = await processarImagem(part.imagem, modo, True)
        await bot.send_photo(chat_id=msg.chat.id, parse_mode='MarkdownV2', photo=imagem_perda,
                             caption=format_text(mbold("Jogo encerrado!")," A resposta era: ",mbold(part.poke),separator=""))
    elif modo == "em cores":
        await bot.send_message(chat_id=msg.chat.id, parse_mode='MarkdownV2',
                               text=format_text(mbold("Jogo encerrado!")," A resposta era: ",mbold(part.poke),separator=""))
    bd.partidas.pop(part.chat)

async def adivinhar(msg):
    msg.text = msg.text.strip().lower()
    part = bd.partidas[chatId(msg)]
    if msg.text == part.poke.lower() and part.acertado == '':
        part.acertado = 's'
        
        await bot.set_message_reaction(msg.chat.id, msg.id, [ReactionTypeEmoji("\U0001F525")], is_big=True)
        await bot.reply_to(msg, parse_mode='MarkdownV2',
                           text=format_text(mbold("Fim da rodada! "),
                                            escape_markdown("Ganhador(a): "),
                                            mbold(msg.from_user.first_name),
                                            escape_markdown("!!"),
                                            separator=""))
        
        addPontos(userId(msg), getData("PLACAR", userId(msg),"ID", "PONTOS")+1)
        part.addPonto(userId(msg))

        part.promise.set()
    
    