# qual-pokemon-bot
Bot em Python criado como projeto da frente Full Stack, do PET Computação ICMC

Agradecimentos ao meu amigo Pozar, que me ajudou a testar o bot.

# Descrição inicial
A proposta do projeto é programar um bot em telegram com o tema "Quem é esse Pokémon?". Ele se consiste em um jogo infinito em que, a cada rodada, algum Pokémon é sorteado e sua imagem é mandada no chat. O primeiro usuário cadastrado que adivinhar corretamente ganha um ponto. Adicionalmente, existe um placar geral de todos os usuários cadastrados no bot, em que cada ponto ganho em cada rodada é contabilizado nesse placar.

O jogo é customizável: Ao utilizar o comando /jogarpoke, é aberto um menu de botões em que o usuário pode selecionar um subconjunto das 9 gerações, o modo de jogo (Original ou Em cores) e o tempo limite de adivinhação até a partida se encerrar (15s, 30s ou 1min).

O bot é programado em Python e foi utilizada a API "pytelegrambot" para intermediar os requests entre a API do Telegram e o programa.

## Funcionamento básico
O bot é feito em Python assíncrono com a biblioteca asyncio.
A API é baseada em handlers cadastrados quando o bot é executado no `main.py`. Cada handler corresponde a um comando (/jogarpoke, /cadastrar, /descadastrar e /placar) ou a um evento (clique nos botões). O arquivo `handlers.py` contém os handlers. O programa utiliza o banco de dados MySQL para gerenciar a pontuação dos usuários no placar geral e uma classe compartilhada em todos os arquivos (a saber, BD) para armazenar as instâncias das partidas acontecendo simultaneamente (as partidas são declaradas sob a classe Partida). O arquivo `variables.py` inicia a conexão com o MySQL, a API e o banco de dados. Todas as outras funções pertinentes para o programa (como a classe Partida e funções que não são os handlers) estão delcaradas no `functions.py`.

O arquivo `pokes.py` contém uma lista com 1025 objetos, representando o nome, a geração e o link do sprite de cada um dos 1025 Pokémon.

## Comandos
Os comandos /cadastrar e /descadastrar adicionam o usuário no MySQL. O Usuário adicionado com o /cadastrar é adicionado na partida que acontece no chat em que ele usa o comando, se houver. O usuário descadastrado não é removido das partidas em que estava participando, apenas do placar geral. A deleção dos dados no placar geral é irreversível.

O comando /placar acessa o MySQL e retorna o placar geral.

O comando /jogarpoke abre o menu para selecionar o modo de jogo. Esse menu é gerenciado com botões da API do Telegram. Por causa de limitações da própria API, não tem como criar handlers personalizados ou temporários de botões, por isso todas as informações referentes às escolhas dos usuários são passadas por meio de uma string que representa o ID de cada botão.

## Modos de jogo
### Original
O modo original enegrece o Pokémon a ponto de se parecer com o modelo visto no anime. Tal manipulação de imagem é feita por meio da API do Pillow, extendida com o PillowAvif para gerenciar alguns sprites que estão em `.avif`, juntamente com a obtenção da imagem feita em request. O bot obtém a imagem, utiliza a função "preencher" para mudar a cor do fundo e posteriormente remover com essa cor específica. A imagem, em PNG e com o contorno em preto, é colada no template `quem.jpeg` e redimensionada para se ajustar ao Telegram. Se ninguém acertar o Pokémon no tempo limite, a mesma imagem, mas sem o processo de escurecimento (ou seja, com o sprite do Pokémon original), é mandada no grupo.
### Em cores
Já o modo em cores é simplesmente o envio do sprite no chat (com as devidas manipulações de tamanho) para o usuário adivinhar seu nome.
Processo similar é feito com a imagem, a diferença é que não há o processo de escurecimento e transformação em PNG, e o Pokémon original não é remandado após a perda.
O nome do Pokémon é mandado no chat quando a partida acaba.

## Restrições
Não tem como iniciar duas partidas no mesmo chat, mas é possível iniciar partidas no privado do bot e em vários chat simultâneos. Usuários não cadastrados podem iniciar o jogo com /jogarpoke, e eles são automaticamente cadastrados após isso. O que o descadastramento faz é não contabilizar a resposta desse usuário, mesmo que esteja correta. Isso foi realizado pois o bot, para acessar as informações do usuário, precisa ter interagido com ele anteriormente, assim o comando serve como forma de interação inicial.
