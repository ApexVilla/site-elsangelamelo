"""Fonte única dos fatos do site.

Regra: só entra aqui o que foi confirmado. Lista vazia = a seção não aparece no
site, e nada de colchete ou texto provisório é publicado. Para publicar um dado
novo: preencher, rodar `python3 .build/build.py` e `python3 .build/validar.py`.
"""
from urllib.parse import quote

SITE = "https://elsangelamelo.com"

NOME = "Elsângela Melo"
PROFISSAO = "Biomédica Esteta"
CRBM = "CRBM 17215"
CLINICA = "Mabelly Aesthetics"
# Como o perfil aparece no Google Maps, e a variação vista no Search Console.
CLINICA_VARIACOES = ["MaBelly Aesthetics", "Ma Belly Aesthetics"]
# Variações de grafia do nome. "elisangela melo" já aparece no Search Console.
NOME_VARIACOES = ["Elisângela Melo", "Elsangela Melo"]

RUA = "R. 240, 308"
BAIRRO = "Setor Coimbra"
CIDADE = "Goiânia"
UF = "GO"
ESTADO = "Goiás"
CEP = "74533-260"
ENDERECO_LINHA = f"{RUA} — {BAIRRO}, {CIDADE} - {UF}, {CEP}"

TEL = "(62) 98202-2330"
TEL_E164 = "+5562982022330"
WHATSAPP = "5562982022330"
EMAIL = "elsangelamelo@gmail.com"
INSTAGRAM = "https://www.instagram.com/elsangelamelo"
INSTAGRAM_H = "@elsangelamelo"
MAPS = "https://maps.app.goo.gl/ZiyC8Jrh5vwLyBqy6"
# Coordenadas do perfil no Google Maps (o valor antigo estava a ~1,4 km dali).
GEO = (-16.6814681, -49.2876674)
MAPA_EMBED = "https://www.google.com/maps?q=MaBelly%20Aesthetics%2C%20R.%20240%2C%20308%20-%20Setor%20Coimbra%2C%20Goi%C3%A2nia&z=16&output=embed"

HORARIO_CURTO = "Seg a sex, 9h às 19h · Sáb, 9h às 14h"
HORARIO_LONGO = "Segunda a sexta, das 9h às 19h. Sábado, das 9h às 14h."

# ─── Analytics ───────────────────────────────────────────────────────────────
# Vazio = nenhum script de terceiro, nenhum cookie e nenhum aviso de cookies.
# Preenchido = aviso de consentimento e GA4 só depois do aceite. Ao preencher,
# ajustar também a CSP: ver .build/deploy/LEIA-ME.md.
GA4_ID = ""

# ─── Aguardando confirmação da profissional (vazio = fora do site) ───────────
# Marcar True só depois de a profissional ter lido e aprovado os textos clínicos.
CONTEUDO_REVISADO = False
# Ex.: [{"valor": "+500", "rotulo": "pacientes atendidas"}]
NUMEROS = []
# Ex.: {"tipo": "Graduação", "curso": "...", "instituicao": "...", "ano": "..."}
FORMACAO = []
# Ex.: {"ano": "...", "titulo": "...", "texto": "..."}
TRAJETORIA = []
# Parágrafos reais de biografia, escritos ou aprovados pela profissional.
BIOGRAFIA = []
# Ex.: {"texto": "...", "nome": "primeiro nome", "tratamento": "..."}
DEPOIMENTOS = []
# Só com autorização por escrito e depois de confirmar as regras do conselho.
# Ex.: {"antes": "/assets/img/...", "depois": "...", "tratamento": "...", "regiao": "...", "intervalo": "..."}
RESULTADOS = []
# Dados do controlador para a política de privacidade.
CONTROLADOR = {"razao_social": "", "cnpj": ""}

TRATAMENTOS = [
    {
        "slug": "harmonizacao-facial", "nome": "Harmonização Facial", "minusculo": "harmonização facial",
        "title": "Harmonização Facial em Goiânia | Elsângela Melo",
        "resumo": "Planejamento que olha o rosto como um conjunto e combina recursos conforme a sua anatomia.",
        "considerar": "proporção e equilíbrio entre os terços do rosto",
        "familia": "injetável",
        "rel": ["preenchimento-labial", "toxina-botulinica", "bioestimuladores"],
        "artigos": ["o-que-e-harmonizacao-facial", "harmonizacao-facial-pode-ficar-natural", "como-escolher-profissional-estetica-facial"],
    },
    {
        "slug": "preenchimento-labial", "nome": "Preenchimento Labial", "minusculo": "preenchimento labial",
        "title": "Preenchimento Labial em Goiânia | Elsângela Melo",
        "resumo": "Ácido hialurônico para trabalhar contorno, hidratação e proporção dos lábios.",
        "considerar": "definição e contorno, respeitando a anatomia da boca",
        "familia": "injetável",
        "rel": ["harmonizacao-facial", "toxina-botulinica", "skinbooster"],
        "artigos": ["cuidados-apos-preenchimento-labial", "botox-e-preenchimento-sao-a-mesma-coisa", "harmonizacao-facial-pode-ficar-natural"],
    },
    {
        "slug": "toxina-botulinica", "nome": "Toxina Botulínica", "minusculo": "toxina botulínica",
        "title": "Toxina Botulínica em Goiânia | Elsângela Melo",
        "resumo": "Reduz temporariamente a contração de músculos específicos e suaviza linhas de expressão.",
        "considerar": "linhas de expressão dinâmicas, em especial no terço superior",
        "familia": "injetável",
        "rel": ["preenchimento-labial", "harmonizacao-facial", "bioestimuladores"],
        "artigos": ["botox-e-preenchimento-sao-a-mesma-coisa", "harmonizacao-facial-pode-ficar-natural", "como-escolher-profissional-estetica-facial"],
    },
    {
        "slug": "bioestimuladores", "nome": "Bioestimuladores de Colágeno", "minusculo": "bioestimuladores de colágeno",
        "title": "Bioestimuladores de Colágeno em Goiânia | Elsângela Melo",
        "resumo": "Estimulam a produção de colágeno pelo próprio organismo, com evolução gradual.",
        "considerar": "flacidez e perda gradual de sustentação",
        "familia": "injetável",
        "rel": ["skinbooster", "harmonizacao-facial", "microagulhamento"],
        "artigos": ["o-que-e-harmonizacao-facial", "como-escolher-profissional-estetica-facial"],
    },
    {
        "slug": "skinbooster", "nome": "Skinbooster", "minusculo": "skinbooster",
        "title": "Skinbooster em Goiânia | Elsângela Melo",
        "resumo": "Microaplicações de ácido hialurônico voltadas à hidratação e à qualidade da pele, sem mudar o contorno.",
        "considerar": "hidratação, maciez e viço da pele",
        "familia": "injetável",
        "rel": ["microagulhamento", "peeling", "bioestimuladores"],
        "artigos": ["como-escolher-profissional-estetica-facial", "o-que-e-harmonizacao-facial"],
    },
    {
        "slug": "peeling", "nome": "Peeling", "minusculo": "peeling",
        "title": "Peeling Facial em Goiânia | Elsângela Melo",
        "resumo": "Renovação controlada das camadas superficiais da pele, com o tipo definido na avaliação.",
        "considerar": "textura irregular, manchas superficiais e aspecto opaco",
        "familia": "superfície",
        "rel": ["microagulhamento", "skinbooster", "bioestimuladores"],
        "artigos": ["como-escolher-profissional-estetica-facial"],
    },
    {
        "slug": "microagulhamento", "nome": "Microagulhamento", "minusculo": "microagulhamento",
        "title": "Microagulhamento em Goiânia | Elsângela Melo",
        "resumo": "Microlesões controladas que estimulam o reparo natural da pele, em sessões espaçadas.",
        "considerar": "textura, cicatrizes de acne e poros dilatados",
        "familia": "superfície",
        "description": "Microagulhamento em Goiânia: como as microlesões controladas estimulam o reparo da pele, para quem pode ser indicado, cuidados e recuperação.",
        "rel": ["peeling", "skinbooster", "bioestimuladores"],
        "artigos": ["como-escolher-profissional-estetica-facial"],
    },
]

ARTIGOS = [
    "cuidados-apos-preenchimento-labial",
    "o-que-e-harmonizacao-facial",
    "botox-e-preenchimento-sao-a-mesma-coisa",
    "harmonizacao-facial-pode-ficar-natural",
    "como-escolher-profissional-estetica-facial",
]

# Ajustes de busca sobre o título e a descrição migrados (dados do Search Console).
ARTIGO_AJUSTES = {
    "cuidados-apos-preenchimento-labial": {
        "title": "Cuidados após preenchimento labial: 24 h, 48 h e 1ª semana",
        "description": "Recomendações pós-preenchimento labial: o que esperar nas primeiras 24 h, 48 h e na primeira semana, quais sinais pedem contato imediato e por que o retorno importa.",
    },
}


def wa(msg=None):
    base = f"https://wa.me/{WHATSAPP}"
    return f"{base}?text={quote(msg, safe='')}" if msg else base


WA_PADRAO = "Olá! Acessei o site da Elsângela Melo e gostaria de informações sobre uma avaliação de estética facial."


def wa_tratamento(minusculo):
    return f"Olá! Acessei o site da Elsângela Melo e gostaria de informações sobre uma avaliação para {minusculo}."


def wa_artigo(titulo):
    return f"Olá! Li o artigo “{titulo}” no site da Elsângela Melo e gostaria de informações sobre uma avaliação."
