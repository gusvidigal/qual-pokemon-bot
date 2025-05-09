from pokes import pokemon_list
from random import choice
import asyncio

import pillow_avif
import requests

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from variables import sql

#Manuseio do MySQL
def addInTable(tabela, dados, args):
    cursor = sql.cursor()
    values = len(args.split(" "))
    values = ", ".join(["%s"]*values)
    comando = "INSERT INTO {} ({}) VALUES ({})".format(tabela, args, values)
    cursor.execute(comando, dados)
    sql.commit()
    cursor.close()
    
def delInTable(tabela, identifier, arg):
    cursor = sql.cursor()
    comando = "DELETE FROM {} WHERE {} = '{}'".format(tabela, arg, identifier)
    cursor.execute(comando)
    sql.commit()
    cursor.close()
    
def addPontos(id, pontos):
    cursor = sql.cursor()
    comando = "UPDATE PLACAR SET PONTOS = {} WHERE ID = '{}'".format(pontos, id)
    cursor.execute(comando)
    sql.commit()
    cursor.close()
    
def getList(tabela, args, unique=False):
    cursor = sql.cursor()
    comando = "SELECT {} FROM {}".format(args, tabela)
    cursor.execute(comando)
    resultado = cursor.fetchall()
    if unique:
        resultado = list(map(lambda l: l[0], resultado))
    return resultado

def getData(tabela, identifier, args, wanted):
    cursor = sql.cursor()
    comando = "SELECT {} FROM {} WHERE {} ='{}'".format(wanted, tabela, args, identifier)
    cursor.execute(comando)
    resultado = cursor.fetchall()
    return resultado[0][0]
                
                
                
                
#Representa uma partida que está acontecendo. Não é salva quando o bot reinicia
class Partida():
    def __init__(self, chat_id, gen=0):
        self.gen = gen
        self.chat = chat_id
        
        self.poke = ''
        self.imagem = ''
        
        self.promise = asyncio.Event()
        self.acertado = ''
        
        self.rodada = 0
        self.placar = []
        
    def escolherPoke(self):
        pokemon_gen = list(filter(lambda p: p["gen"] in self.gen, pokemon_list))
        pokemon = choice(pokemon_gen)
        
        self.poke = pokemon["poke"]
        self.imagem = pokemon["imagem"]

    async def timeout(self, rod, tempo):
        await asyncio.sleep(tempo)
        if rod == self.rodada and self.acertado == '':
            self.acertado = 'n'
            self.promise.set()
            
    def addPonto(self, identifier):
        flag = False
        for dic in self.placar:
            if dic["id"] == identifier:
                flag = True
                dic["pontos"] += 1
        if not flag:
            nome = getData("PLACAR", identifier, "ID", "NOME")
            self.placar.append({"nome": nome, "id": identifier, "pontos": 1})
                
                

async def processarImagem(link, modo, perda=False):
    
    request_img = requests.get(link)
    imagem = Image.open(BytesIO(request_img.content)).convert("RGBA")
    if modo == "original":
        # Utiliza um balde para pintar o fundo branco de magenta
        # para posteriormente converter o não-magenta em preto e magenta em branco.
        ImageDraw.floodfill(imagem, xy=(0,0), value=(255, 0, 255, 255), thresh=200)
        
        pixels = imagem.getdata()
        novos_pixels = []
        for p in pixels:
            if p[0] != 255 or p[1] != 0 or p[2] != 255:
                if perda:
                    novos_pixels.append((p[0], p[1], p[2], 255))
                else:
                    novos_pixels.append((44, 51, 69, 255))
            else:
                novos_pixels.append((255,255,255, 0))
        imagem.putdata(novos_pixels)

        #Redimensionar imagem
        imagem.thumbnail((275, 275))
        #borda = 10px
        #Edição do template. Centro: 170,170
        template = Image.open('quem.jpg').convert("RGBA")
        template.paste(imagem, (170-int(imagem.width/2), 170-int(imagem.height/2)), imagem)
        imagem = template

    elif modo == "em cores":
        #Redimensionar imagem
        imagem.thumbnail((300, 300))
        #borda = 10px
        imagem_quadrada = Image.new("RGB",(320,320), (255,255,255))
        imagem_quadrada.paste(imagem, (160-int(imagem.width/2), 160-int(imagem.height/2)), imagem)
        imagem = imagem_quadrada
        
    #img = ImageDraw.Draw(imagem)
    #img.text((10, imagem.height-10-int(imagem.height/15)),
    #         "@qualpokemon_bot",
    #         font=ImageFont.truetype('arial.ttf', int(imagem.height/15)),
    #         fill =(0, 0, 0))

    bio = BytesIO()
    bio.name = 'imagem.png'
    imagem.save(bio, format='PNG')
    bio.seek(0)
    return bio

def chatId(msg):
    return str(msg.chat.id)
def userId(msg):
    return str(msg.from_user.id)

def gerarPlacar(placar):
    placar.sort(key=lambda dic: dic["pontos"], reverse=True)

    lista = list(map(lambda dic: '[{}](tg://user?id={}): {}'.format(dic["nome"].replace("-", "\\-"),dic["id"],dic["pontos"]), placar))
    if len(lista)>2:
        lista[2] = '🥉' + lista[2]
    if len(lista)>1:
        lista[1] = '🥈' + lista[1]
    if len(lista)>0:
        lista[0] = '🥇' + lista[0]
            
    texto_placar = '\n'.join(lista)
    
    return texto_placar
 
                