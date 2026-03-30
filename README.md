# Jokenpô
um jogo desktop desenvolvido em Python que traz o clássico "Pedra, Papel e Tesoura" para um ambiente interativo com interface gráfica. O projeto se destaca por integrar conceitos avançados de programação, como Estruturas de Dados, Redes e Inteligência Artificial.

Principais Tecnologias Utilizadas:

Interface Gráfica (GUI): Construída com a biblioteca padrão tkinter. Possui um visual moderno em modo escuro (utilizando paletas de cores customizadas, semelhantes ao tema Catppuccin).

Estrutura de Dados Customizada: O histórico de rodadas de uma partida não usa listas comuns do Python, mas sim uma Lista Encadeada (ListaEncadeada e classe No) construída do zero para registrar inclusões, exclusões (empates são anulados e removidos da lista) e consultas de vitórias.

Inteligência Artificial (Aprendizado por Reforço): No modo singleplayer, você joga contra um "Robô Hacker". Ele utiliza um sistema de memória (uma versão simplificada de Q-Learning/Q-Table) que anota as jogadas que dão certo ou errado contra você, aprendendo seus padrões e ficando mais inteligente a cada rodada.

Multiplayer Local (LAN): Através da biblioteca socket e threading, o jogo permite que um jogador "Hospede" uma sala e outro se "Conecte" via rede Wi-Fi ou cabo usando um código curto gerado a partir do IP local.

Arquitetura dos Arquivos:

main.py: O ponto de entrada que inicia a janela principal do jogo.

jogo_gui.py: Contém a lógica principal do jogo, o menu, o gerenciamento da rede, as regras da IA e a construção das telas.

estruturas.py: Contém as classes voltadas para a manipulação dos dados das rodadas (Rodada, No, ListaEncadeada).

interface.py: Focado em criar janelas secundárias (Modais) para interações rápidas, como inserir nomes/códigos e exibir os resultados.
