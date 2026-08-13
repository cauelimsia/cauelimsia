# tools/

## `gen_cards.py`

Gera o banner deste perfil e os **social previews** (a imagem que o GitHub mostra quando
alguém compartilha o link de um repositório) de todos os repos públicos.

```bash
pip install pillow
python tools/gen_cards.py
```

As fontes Poppins são baixadas na primeira execução. A saída vai para `tools/cards/`.

### Identidade

Segue o sistema visual do **[cauedev.shop](https://cauedev.shop)** — os tokens saem de
`DESIGN.md` e `src/styles/main.css` daquele projeto. Quem sai do GitHub para o site sente a
mesma mão.

| Elemento | Decisão |
|---|---|
| Linguagem | neubrutalismo: borda ink, cor chapada, sombra dura **sem blur** |
| Fundo | `--cream #f5f2ea` com a malha azul do hero a 5% |
| Card | `--paper #fff`, borda ink, sombra deslocada, radius 18 |
| Cor | tríade fixa `--blue #125cfe` · `--lime #ccff00` · `--coral #ff4d4d` |
| Tipografia | Space Grotesk 700 no display (tracking −0.035em), Inter no corpo |
| Motivo | selo girado −8°, como os stickers do hero |
| Formato | 1280×640 no social preview, 1280×460 no banner |

**A marca Atlas não entra aqui.** Sem mascote robô, sem lockup, sem o nome — o perfil se
apresenta como pessoa procurando vaga, não como agência. O que atravessa é só a linguagem
visual.

A paleta é fixa de propósito: o que muda por repositório é **qual acento lidera** e o texto
do selo. Cor arbitrária por projeto quebraria a família.

A cor do texto sobre preenchimento chapado é escolhida por contraste (`on()`), não à mão:
preto sobre o azul da marca dá 4.0:1 e branco dá 5.2:1, então azul pede branco enquanto lime
e coral pedem preto.

### Adicionando um repo novo

Acrescente uma tupla em `CARDS` — `(arquivo, título, subtítulo, [chips], acento)` — e rode
de novo. Depois suba a imagem em **Settings → Social preview** do repositório
(o GitHub não expõe isso por API; o upload é pela interface).

> Repositório privado não tem a seção de social preview: ela só aparece depois que o repo
> vira público.
