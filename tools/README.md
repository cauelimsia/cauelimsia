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

Todos os cards saem da mesma composição, para que leiam como família quando aparecem juntos:

| Elemento | Decisão |
|---|---|
| Fundo | gradiente `#070B16 → #0D1426` |
| Textura | malha de pontos a 34px, 4% de opacidade |
| Motivo | nuvem gaussiana de partículas à direita — o mesmo organismo do deck [redecorr-apresentacao](https://github.com/cauelimsia/redecorr-apresentacao) |
| Tipografia | Poppins (ExtraBold no título, Regular no texto, SemiBold nos chips) |
| Acento | uma cor por projeto, aplicada na barra da esquerda, na régua, nos chips e nas partículas |
| Formato | 1280×640 para social preview, 1280×440 para o banner do perfil |

### Adicionando um repo novo

Acrescente uma tupla em `CARDS` — `(arquivo, título, subtítulo, [chips], acento)` — e rode
de novo. Depois suba a imagem em **Settings → Social preview** do repositório
(o GitHub não expõe isso por API; o upload é pela interface).

> Repositório privado não tem a seção de social preview: ela só aparece depois que o repo
> vira público.
