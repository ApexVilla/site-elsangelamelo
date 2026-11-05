#!/usr/bin/env python3
"""Gera o site estático de elsangelamelo.com.

A raiz do repositório continua sendo o artefato servido pelo nginx: sem Node e sem
build em produção. Este script só evita copiar cabeçalho, rodapé e dados em cada
página. Pastas ocultas (.build, .docs) são bloqueadas pelo nginx.

Uso:  python3 .build/build.py  &&  python3 .build/validar.py
"""
import datetime
import hashlib
import html
import json
import pathlib
import re
import shutil
import sys
import unicodedata

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BUILD = RAIZ / ".build"
sys.path.insert(0, str(BUILD))

import dados as D  # noqa: E402
import figuras as F  # noqa: E402

HOJE = datetime.date.today().isoformat()
MESES = "janeiro fevereiro março abril maio junho julho agosto setembro outubro novembro dezembro".split()

SETA = '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M1 8h13M9.5 3.5 14 8l-4.5 4.5"/></svg>'
ICONE_WA = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M17.5 14.4c-.3-.2-1.7-.9-2-1-.3-.1-.5-.1-.6.2-.2.3-.7.9-.9 1.1-.2.2-.3.2-.6.1-.3-.2-1.2-.5-2.3-1.4-.9-.8-1.4-1.7-1.6-2-.2-.3 0-.5.1-.6l.4-.5.3-.5v-.5c0-.2-.6-1.5-.9-2.1-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.5.1-.7.3-.3.3-.9.9-.9 2.2s.9 2.5 1.1 2.7c.1.2 1.8 2.8 4.4 3.9.6.3 1.1.4 1.5.5.6.2 1.2.2 1.6.1.5-.1 1.7-.7 1.9-1.3.2-.7.2-1.2.2-1.3-.1-.2-.3-.2-.6-.4M12 2a10 10 0 0 0-8.5 15.2L2 22l4.9-1.3A10 10 0 1 0 12 2m0 18.2c-1.5 0-3-.4-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2"/></svg>'
ICONE_AVISO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 7.6v.6"/></svg>'
PINO = '<svg class="mapa-g__pino" viewBox="0 0 28 36" fill="none" stroke="currentColor" stroke-width="1.2" aria-hidden="true"><path d="M14 35S1 21.5 1 13a13 13 0 0 1 26 0c0 8.500-13 22-13 22Z"/><circle cx="14" cy="13" r="4"/></svg>'

ALT_GLOBO = "Retrato de estúdio de Elsângela Melo, biomédica esteta, segurando um globo facial de cristal rosa diante do rosto"
ALT_OCULOS = "Retrato de estúdio de Elsângela Melo, biomédica esteta, de óculos e conjunto rosa"
AVISO_PADRAO = "Este conteúdo é informativo e educativo. Não constitui diagnóstico, prescrição ou promessa de resultado e não substitui a avaliação presencial. Indicações, contraindicações e condutas são definidas individualmente, em consulta com profissional habilitado."


def esc(s):
    return html.escape(s, quote=True)


def puro(h):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", h))).strip()


def slugify(s):
    s = unicodedata.normalize("NFKD", puro(s)).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:70]


def data_br(iso):
    a, m, d = iso.split("-")
    return f"{int(d)} de {MESES[int(m) - 1]} de {a}"


def hash_de(b):
    return hashlib.sha256(b if isinstance(b, bytes) else b.encode()).hexdigest()[:10]


def fragmento(rel):
    bruto = (BUILD / "paginas" / rel).read_text(encoding="utf-8")
    m = re.match(r"<!--meta\n(.*?)\n-->\n", bruto, re.S)
    return json.loads(m[1]), bruto[m.end():], hash_de(bruto)


# ─── Datas reais de atualização ──────────────────────────────────────────────
ARQ_DATAS = BUILD / "datas.json"
DATAS = json.loads(ARQ_DATAS.read_text()) if ARQ_DATAS.exists() else {}


def data_pagina(url, assinatura):
    """A data só muda quando o conteúdo muda: o lastmod do sitemap fica verdadeiro."""
    atual = DATAS.get(url)
    if not atual or atual["assinatura"] != assinatura:
        DATAS[url] = {"assinatura": assinatura, "data": HOJE}
    return DATAS[url]["data"]


# ─── Assets ──────────────────────────────────────────────────────────────────
def minificar_css(c):
    c = re.sub(r"/\*.*?\*/", "", c, flags=re.S)
    c = re.sub(r"\s+", " ", c)
    return re.sub(r"\s*([{};,>])\s*", r"\1", c).replace(";}", "}").strip()


def publicar_assets():
    pasta = RAIZ / "assets"
    for velho in list(pasta.glob("site.*.css")) + list(pasta.glob("site.*.js")):
        velho.unlink()
    css = minificar_css((BUILD / "estilo.css").read_text(encoding="utf-8"))
    js = (BUILD / "site.js").read_text(encoding="utf-8")
    js = re.sub(r"/\*.*?\*/", "", js, flags=re.S)
    js = "\n".join(l.strip() for l in js.splitlines() if l.strip())
    nome_css, nome_js = f"site.{hash_de(css)}.css", f"site.{hash_de(js)}.js"
    (pasta / nome_css).write_text(css, encoding="utf-8")
    (pasta / nome_js).write_text(js, encoding="utf-8")
    (pasta / "rosto").mkdir(exist_ok=True)
    versao = hash_de("".join(F.svg_arquivo(s) for s in F.REGIOES))
    for slug in F.REGIOES:
        (pasta / "rosto" / f"{slug}.svg").write_text(F.svg_arquivo(slug), encoding="utf-8")
    for velho in pasta.glob("lenis.*.js"):
        velho.unlink()
    lenis = (BUILD / "vendor" / "lenis-1.3.27.min.js").read_bytes()
    nome_lenis = f"lenis.{hash_de(lenis)}.js"
    (pasta / nome_lenis).write_bytes(lenis)
    return f"/assets/{nome_css}", f"/assets/{nome_js}", versao, f"/assets/{nome_lenis}"


CSS, JS, V_ROSTO, LENIS = None, None, None, None


def rosto(slug):
    return f"/assets/rosto/{slug}.svg?v={V_ROSTO}"


# ─── Dados estruturados ──────────────────────────────────────────────────────
ID_PESSOA = f"{D.SITE}/#elsangela"
ID_CLINICA = f"{D.SITE}/#clinica"
ID_SITE = f"{D.SITE}/#site"
FOTO_URL = f"{D.SITE}/assets/img/retrato-oculos-682.webp"


def ld_pessoa():
    return {
        "@type": "Person", "@id": ID_PESSOA, "name": D.NOME, "alternateName": D.NOME_VARIACOES,
        "jobTitle": D.PROFISSAO,
        "identifier": {"@type": "PropertyValue", "name": "CRBM-3", "value": D.CRBM.split()[-1]},
        "description": "Biomédica esteta com atuação em estética facial em Goiânia, Goiás, com atendimento na MaBelly Aesthetics, no Setor Coimbra.",
        "url": f"{D.SITE}/sobre/", "image": FOTO_URL, "telephone": D.TEL_E164,
        "worksFor": {"@id": ID_CLINICA}, "workLocation": {"@id": ID_CLINICA},
        "knowsAbout": [t["nome"] for t in D.TRATAMENTOS], "sameAs": [D.INSTAGRAM],
    }


def ld_clinica():
    return {
        "@type": "HealthAndBeautyBusiness", "@id": ID_CLINICA, "name": D.CLINICA, "alternateName": D.CLINICA_VARIACOES,
        "description": "Local de atendimento de estética facial de Elsângela Melo, biomédica esteta, em Goiânia.",
        "url": f"{D.SITE}/contato/", "telephone": D.TEL_E164, "email": D.EMAIL, "image": FOTO_URL,
        "address": {"@type": "PostalAddress", "streetAddress": f"{D.RUA} - {D.BAIRRO}", "addressLocality": D.CIDADE,
                    "addressRegion": D.UF, "postalCode": D.CEP, "addressCountry": "BR"},
        "geo": {"@type": "GeoCoordinates", "latitude": D.GEO[0], "longitude": D.GEO[1]},
        "hasMap": D.MAPS,
        "areaServed": {"@type": "City", "name": D.CIDADE, "containedInPlace": {"@type": "State", "name": D.ESTADO}},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "09:00", "closes": "19:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "09:00", "closes": "14:00"},
        ],
        "employee": {"@id": ID_PESSOA},
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Tratamentos de estética facial", "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": t["nome"], "url": f"{D.SITE}/{t['slug']}/"}} for t in D.TRATAMENTOS]},
        "sameAs": [D.INSTAGRAM],
    }


def ld_site():
    return {"@type": "WebSite", "@id": ID_SITE, "url": f"{D.SITE}/", "name": "Elsângela Melo — Biomédica Esteta",
            "alternateName": D.NOME, "inLanguage": "pt-BR", "publisher": {"@id": ID_PESSOA}}


def ld_pagina(url, titulo, descricao, tipo="WebPage", data=None, sobre=None):
    d = {"@type": tipo, "@id": f"{D.SITE}{url}#pagina", "url": f"{D.SITE}{url}", "name": titulo, "description": descricao,
         "inLanguage": "pt-BR", "isPartOf": {"@id": ID_SITE, "@type": "WebSite", "url": f"{D.SITE}/", "name": "Elsângela Melo — Biomédica Esteta"}}
    if data:
        d["dateModified"] = data
    if sobre:
        d["about"] = sobre
    return d


def ld_migalhas(itens):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": puro(n), "item": f"{D.SITE}{u}"} for i, (n, u) in enumerate(itens)]}


def ld_faq(corpo):
    pares = re.findall(r"<summary>(.*?)</summary>\s*<div class=\"faq__body\">(.*?)</div>\s*</details>", corpo, re.S)
    if not pares:
        return None
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": puro(p), "acceptedAnswer": {"@type": "Answer", "text": puro(r)}} for p, r in pares]}


def bloco_ld(grafo):
    limpo = [g for g in grafo if g]
    return ('<script type="application/ld+json">'
            + json.dumps({"@context": "https://schema.org", "@graph": limpo}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
            + "</script>")


# ─── Peças ───────────────────────────────────────────────────────────────────
NAV = [("/tratamentos/", "Tratamentos"), ("/sobre/", "Sobre"), ("/resultados/", "Resultados"), ("/blog/", "Blog"), ("/contato/", "Contato")]


def head(p):
    url = p["url"]
    canon = f'<link rel="canonical" href="{D.SITE}{url}">' if p.get("canonical", True) else ""
    img = p.get("og_imagem", "/og-image.jpg")
    ga = f'<meta name="analytics-id" content="{esc(D.GA4_ID)}">' if D.GA4_ID else ""
    return f"""<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(p['title'])}</title>
<meta name="description" content="{esc(p['description'])}">
<meta name="robots" content="{p.get('robots', 'index, follow, max-image-preview:large')}">
{canon}
<meta name="author" content="{D.NOME}">
<meta name="theme-color" content="#FDFCFC">
<meta property="og:type" content="{p.get('og_tipo', 'website')}">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Elsângela Melo — Biomédica Esteta">
<meta property="og:url" content="{D.SITE}{url}">
<meta property="og:title" content="{esc(p['title'])}">
<meta property="og:description" content="{esc(p['description'])}">
<meta property="og:image" content="{D.SITE}{img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(p.get('og_alt', 'Elsângela Melo, biomédica esteta em Goiânia'))}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(p['title'])}">
<meta name="twitter:description" content="{esc(p['description'])}">
<meta name="twitter:image" content="{D.SITE}{img}">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" href="/assets/fonts/bodoni-moda.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/hanken-grotesk.woff2" as="font" type="font/woff2" crossorigin>
{p.get('preload', '')}
<link rel="stylesheet" href="{CSS}">
<script src="{JS}" defer data-lenis="{LENIS}"></script>
{ga}
{bloco_ld(p['ld']) if p.get('ld') else ''}
</head>"""


def cabecalho(atual):
    corrente = ' aria-current="page"'
    itens = "".join(f'<li><a href="{u}"{corrente if u == atual else ""}>{n}</a></li>' for u, n in NAV)
    return f"""<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header class="topo">
  <div class="progresso" aria-hidden="true"><span></span></div>
  <div class="casco">
    <a class="marca" href="/">
      <img class="marca__em" src="/assets/icons/em.svg" width="36" height="36" alt="">
      <span><span class="marca__nome">{D.NOME}</span><span class="marca__funcao">{D.PROFISSAO}</span></span><span class="visualmente-oculto">, página inicial</span>
    </a>
    <button class="menu-botao" type="button" aria-expanded="false" aria-controls="menu" aria-label="Abrir menu">
      <svg viewBox="0 0 26 26" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><line class="l1" x1="3" y1="9" x2="23" y2="9"/><line class="l2" x1="3" y1="17" x2="23" y2="17"/></svg>
    </button>
    <nav class="menu" id="menu" aria-label="Principal" data-aberto="false">
      <ul class="menu__lista">{itens}</ul>
      <a class="btn menu__cta" data-origem="menu" href="{esc(D.wa(D.WA_PADRAO))}" rel="noopener">Agendar avaliação</a>
      <div class="menu__rodape">
        <a class="btn" data-origem="menu-movel" href="{esc(D.wa(D.WA_PADRAO))}" rel="noopener">{ICONE_WA} Agendar avaliação</a>
        <p>{D.CLINICA} · {D.BAIRRO}, {D.CIDADE}<br>{D.HORARIO_CURTO}</p>
      </div>
    </nav>
  </div>
</header>"""


def rodape():
    trat = "".join(f'<li><a href="/{t["slug"]}/">{t["nome"]}</a></li>' for t in D.TRATAMENTOS)
    cookies = '<button type="button" data-preferencias-cookies>Preferências de cookies</button>' if D.GA4_ID else ""
    return f"""<footer class="rodape">
  <div class="casco">
    <div class="rodape__grade">
      <div>
        <p class="rodape__marca">{D.NOME}</p>
        <p class="rodape__funcao">{D.PROFISSAO} · {D.CRBM}</p>
        <p>Estética facial em Goiânia, com avaliação individual e planejamento conforme a anatomia de cada rosto.</p>
      </div>
      <nav aria-label="Tratamentos"><h2>Tratamentos</h2><ul>{trat}</ul></nav>
      <nav aria-label="Navegação do site"><h2>Navegação</h2><ul>
        <li><a href="/">Início</a></li><li><a href="/sobre/">Sobre Elsângela</a></li><li><a href="/tratamentos/">Todos os tratamentos</a></li>
        <li><a href="/resultados/">Resultados</a></li><li><a href="/blog/">Blog</a></li><li><a href="/contato/">Contato</a></li>
      </ul></nav>
      <div><h2>Atendimento</h2>
        <address>{D.CLINICA}<br>{D.RUA} — {D.BAIRRO}<br>{D.CIDADE} - {D.UF}, {D.CEP}</address>
        <ul>
          <li><a href="{D.MAPS}" rel="noopener">Como chegar</a></li>
          <li><a href="tel:{D.TEL_E164}">{D.TEL}</a></li>
          <li><a href="mailto:{D.EMAIL}">{D.EMAIL}</a></li>
          <li><a href="{D.INSTAGRAM}" rel="noopener">Instagram {D.INSTAGRAM_H}</a></li>
        </ul>
        <p>{D.HORARIO_CURTO}</p>
      </div>
    </div>
    <div class="rodape__base">
      <p>© {HOJE[:4]} {D.NOME} — {D.PROFISSAO}.</p>
      <p><a href="/politica-de-privacidade/">Política de Privacidade</a> {cookies}</p>
    </div>
  </div>
</footer>
<aside aria-label="Contato rápido"><a class="wa-flutuante" data-origem="flutuante" href="{esc(D.wa(D.WA_PADRAO))}" rel="noopener" aria-label="Falar no WhatsApp">{ICONE_WA}</a></aside>"""


def documento(p, corpo, atual=None, sem_moldura=False, atributos=""):
    if sem_moldura:
        return f'<!doctype html>\n<html lang="pt-BR">\n{head(p)}\n<body class="corpo-links"{atributos}>\n{corpo}\n</body>\n</html>\n'
    return f'<!doctype html>\n<html lang="pt-BR">\n{head(p)}\n<body{atributos}>\n{cabecalho(atual)}\n{corpo}\n{rodape()}\n</body>\n</html>\n'


def migalhas(itens):
    li = []
    for i, (nome, url) in enumerate(itens):
        li.append(f'<li><span aria-current="page">{nome}</span></li>' if i == len(itens) - 1 else f'<li><a href="{url}">{nome}</a></li>')
    return f'<nav class="migalhas" aria-label="Você está aqui"><ol>{"".join(li)}</ol></nav>'


def btn_wa(rotulo, msg, origem, classe="btn"):
    return f'<a class="{classe}" data-origem="{origem}" href="{esc(D.wa(msg))}" rel="noopener">{ICONE_WA} {rotulo}</a>'


def seta(rotulo, url, extra=""):
    return f'<a class="seta" href="{esc(url)}"{extra}>{rotulo} {SETA}</a>'


def aviso(texto=AVISO_PADRAO):
    return f'<div class="aviso">{ICONE_AVISO}<p>{texto}</p></div>'


def indice(corpo):
    """Dá âncora a cada h2 e monta o índice da página a partir deles."""
    usados, itens = set(), []

    def trocar(m):
        texto = m[2]
        ancora = slugify(texto) or "secao"
        while ancora in usados:
            ancora += "-2"
        usados.add(ancora)
        itens.append((ancora, puro(texto)))
        return f'<h2 id="{ancora}">{texto}</h2>'

    novo = re.sub(r"<h2( [^>]*)?>(.*?)</h2>", trocar, corpo, flags=re.S)
    lista = "".join(f'<li><a href="#{a}">{esc(t)}</a></li>' for a, t in itens)
    nav = f'<details class="indice"><summary>Nesta página</summary><nav aria-label="Nesta página"><ol>{lista}</ol></nav></details>'
    return novo, nav


def foto_oculos(sizes, lazy=True, classe=""):
    carga = 'loading="lazy" decoding="async"' if lazy else 'fetchpriority="high"'
    return (f'<img class="{classe}" src="/assets/img/retrato-oculos-682.webp" srcset="/assets/img/retrato-oculos-420.webp 420w, '
            f'/assets/img/retrato-oculos-682.webp 682w" sizes="{sizes}" width="682" height="1024" {carga} alt="{ALT_OCULOS}">')


def bloco_profissional():
    return f"""<section class="sec sec--branca sec--curta fio-topo">
  <div class="casco profissional revela">
    <div class="profissional__foto paralaxe">{foto_oculos("(min-width: 760px) 224px, 60vw")}</div>
    <div class="profissional__texto">
      <p class="rubrica">Quem realiza o atendimento</p>
      <h2>{D.NOME}</h2>
      <p class="sobre__registro">Biomédica esteta · {D.CRBM}</p>
      <p>{D.NOME} é formada como biomédica esteta e atua com estética facial em Goiânia, na {D.CLINICA}, no {D.BAIRRO}. Cada atendimento parte de uma avaliação presencial, individual e gratuita.</p>
      <div>{seta("Conhecer a profissional", "/sobre/")}</div>
    </div>
  </div>
</section>"""


def bloco_local(titulo="Atendimento em Goiânia, no Setor Coimbra"):
    return f"""<section class="sec sec--curta fio-topo">
  <div class="casco revela">
    <div class="cabeca revela"><p class="rubrica">Localização</p><h2>{titulo}</h2></div>
    <div class="local__dados grade-liga grade-liga--3">
      <div><h3>Endereço</h3><address>{D.CLINICA}<br>{D.RUA} — {D.BAIRRO}<br>{D.CIDADE} - {D.UF}, {D.CEP}</address></div>
      <div><h3>Horário</h3><p>Segunda a sexta, das 9h às 19h<br>Sábado, das 9h às 14h</p></div>
      <div><h3>Contato</h3><p><a href="tel:{D.TEL_E164}">{D.TEL}</a><br>{seta("Como chegar", D.MAPS, ' rel="noopener"')}</p></div>
    </div>
  </div>
</section>"""


def bloco_mapa_google():
    return f"""<div class="mapa-g" data-mapa-google="{esc(D.MAPA_EMBED)}">
  <div class="mapa-g__capa">
    {PINO}
    <strong>{D.CLINICA}</strong>
    <p>{D.RUA} — {D.BAIRRO}, {D.CIDADE}</p>
    <button class="btn btn--fio" type="button">Mostrar mapa</button>
    <p>O mapa é do Google e só carrega se você pedir, para que nenhum dado seja enviado antes disso.</p>
  </div>
</div>"""


def faixa_cta(texto, msg, origem):
    return f"""<section class="sec sec--escuro" data-cortina>
  <div class="casco cabeca revela" style="margin-bottom:0">
    <p class="rubrica">Próximo passo</p>
    <h2>O primeiro passo é <em>uma conversa</em></h2>
    <p class="chamada">{texto} A avaliação é gratuita.</p>
    <div class="acoes">
      {btn_wa("Agendar avaliação", msg, origem, "btn btn--claro")}
      <a class="btn btn--fio-claro" href="/contato/">Outras formas de contato</a>
    </div>
  </div>
</section>"""


def ligacao(tipo, titulo, resumo, url):
    return f'<a class="liga" href="{url}"><span class="liga__tipo">{tipo}</span><h3><span>{titulo}</span></h3><p>{resumo}</p></a>'


def formulario(agendamento=False):
    opcoes = '<option value="Avaliação geral" data-slug="geral">Avaliação geral</option>' + "".join(
        f'<option value="{t["nome"]}" data-slug="{t["slug"]}">{t["nome"]}</option>' for t in D.TRATAMENTOS) + '<option value="Outro" data-slug="outro">Outro</option>'
    extras = ""
    if agendamento:
        extras = """<div class="campo"><label for="data">Data de preferência (opcional)</label>
      <input id="data" name="data" type="date" aria-describedby="ajuda-data"><small id="ajuda-data">É só uma preferência: o horário é confirmado pelo WhatsApp. Atendimento de segunda a sábado.</small></div>
    <fieldset class="opcoes"><legend>Período de preferência (opcional)</legend>
      <label class="opcao"><input type="radio" name="periodo" value="Manhã"> Manhã</label>
      <label class="opcao"><input type="radio" name="periodo" value="Tarde"> Tarde</label>
    </fieldset>"""
    return f"""<form class="form" data-form-avaliacao data-whatsapp="{D.WHATSAPP}" novalidate>
    <div class="campo"><label for="nome">Nome</label>
      <input id="nome" name="nome" type="text" autocomplete="name" required aria-describedby="erro-nome"><p class="campo__erro" id="erro-nome"></p></div>
    <div class="campo"><label for="telefone">WhatsApp com DDD</label>
      <input id="telefone" name="telefone" type="tel" inputmode="tel" autocomplete="tel-national" required aria-describedby="erro-telefone"><p class="campo__erro" id="erro-telefone"></p></div>
    <div class="campo"><label for="interesse">Tratamento de interesse</label>
      <select id="interesse" name="interesse" required aria-describedby="erro-interesse">{opcoes}</select><p class="campo__erro" id="erro-interesse"></p></div>
    {extras}
    <div class="campo"><label for="mensagem">Mensagem (opcional)</label>
      <textarea id="mensagem" name="mensagem" rows="3" aria-describedby="ajuda-mensagem"></textarea>
      <small id="ajuda-mensagem">Não é preciso contar detalhes de saúde aqui: isso é conversado na avaliação.</small></div>
    <div class="campo"><label class="aceite"><input type="checkbox" name="consentimento" required aria-describedby="erro-consentimento">
      <span>Concordo com o uso destes dados para responder ao meu contato, conforme a <a href="/politica-de-privacidade/">Política de Privacidade</a>.</span></label>
      <p class="campo__erro" id="erro-consentimento"></p></div>
    <button class="btn btn--inteiro __BOTAO__" type="submit">{ICONE_WA} Continuar no WhatsApp</button>
    <p class="form__nota">O formulário abre uma conversa no WhatsApp com a mensagem pronta. Nada é gravado neste site.</p>
    <p class="form__status" data-form-status tabindex="-1" role="status" hidden>Abrimos o WhatsApp com a sua mensagem pronta: falta só tocar em enviar. Se não abriu, <a href="{D.wa()}" target="_blank" rel="noopener">abra a conversa aqui</a>.</p>
    <noscript><p class="form__nota">Se o formulário não funcionar no seu navegador, fale direto pelo <a href="{esc(D.wa(D.WA_PADRAO))}" rel="noopener">WhatsApp</a>.</p></noscript>
  </form>"""


def secao_form(titulo="O primeiro passo é <em>uma conversa</em>", texto=None, agendamento=False, ancora="avaliacao"):
    texto = texto or "A avaliação é gratuita. É o momento de entender o que é indicado para o seu rosto, sem compromisso de realizar qualquer procedimento no mesmo dia."
    return f"""<section class="sec sec--escuro" id="{ancora}" data-cortina>
  <div class="casco cta-final revela">
    <div class="cta-final__texto">
      <p class="rubrica">Solicite uma avaliação</p>
      <h2>{titulo}</h2>
      <p class="chamada">{texto}</p>
      <p class="chamada">Prefere escrever direto? <a href="{esc(D.wa(D.WA_PADRAO))}" data-origem="form-direto" rel="noopener">{D.TEL} no WhatsApp</a>.</p>
    </div>
    {formulario(agendamento).replace("__BOTAO__", "btn--claro")}
  </div>
</section>"""


PASSOS = [
    ("Seus objetivos", "Conversa sobre o que incomoda, há quanto tempo e o que você espera."),
    ("Avaliação", "Análise do rosto em repouso e em movimento, com histórico de saúde e procedimentos anteriores."),
    ("Possibilidades", "Explicação dos caminhos possíveis, com os limites e os cuidados de cada um."),
    ("Plano", "Definição do planejamento, quando houver indicação, e dos valores correspondentes."),
    ("Acompanhamento", "Orientações antes e depois, com retorno para avaliar a evolução."),
]


def lista_passos():
    return '<ol class="passos">' + "".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a, b in PASSOS) + "</ol>"


def palavras(h):
    """Envolve cada palavra em um span, sem tocar nas tags, para acender ao rolar."""
    partes = re.split(r"(<[^>]+>)", h)
    return "".join(p if p.startswith("<") else re.sub(r"(\S+)", r'<span class="palavra">\1</span>', p) for p in partes)


def secao_passos():
    return f"""<section class="sec pista" id="avaliacao" data-pista>
  <div class="pista__fixo">
    <div class="casco">
      <div class="cabeca revela">
        <p class="rubrica">Passo a passo</p>
        <h2>Como funciona a avaliação</h2>
        <p class="chamada">A avaliação é gratuita e conduzida sem pressa, sem compromisso de fazer qualquer procedimento no mesmo dia.</p>
      </div>
    </div>
    <div class="casco-pista">{lista_passos()}</div>
    <div class="pista__barra" aria-hidden="true"><span></span></div>
  </div>
</section>"""


# ─── Páginas ─────────────────────────────────────────────────────────────────
def pagina_home():
    url = "/"
    title = "Elsângela Melo | Biomédica Esteta em Goiânia"
    desc = "Elsângela Melo, biomédica esteta em Goiânia. Harmonização facial, preenchimento labial, toxina botulínica e bioestimuladores, com avaliação gratuita no Setor Coimbra."
    _, faq, _ = fragmento("_faq-home.html")
    linhas = []
    for i, t in enumerate(D.TRATAMENTOS):
        s = t["slug"]
        ativa = " is-ativa" if i == 0 else ""
        linhas.append(f"""<article class="linha{ativa}" data-regiao="{s}" data-nome="{esc(t['nome'])}" data-rotulo="{esc(F.ROTULOS[s])}">
        <span class="linha__n">0{i + 1}</span>
        <h3><a href="/{s}/">{t['nome']}</a></h3>
        <img class="linha__mini" src="{rosto(s)}" width="84" height="109" loading="lazy" decoding="async" alt="Ilustração do rosto que destaca {esc(F.ROTULOS[s])}">
        <p>{t['resumo']}</p>
        <p class="linha__considerar"><b>Pode ser considerado para:</b> {t['considerar']}.</p>
        <div class="linha__acoes">{seta("Entender o tratamento", f"/{s}/")}<a class="seta" data-origem="home-{s}" href="{esc(D.wa(D.wa_tratamento(t['minusculo'])))}" rel="noopener">Perguntar no WhatsApp</a></div>
      </article>""")
    grupos = F.svg_interativo().replace('class="r-grupo" data-regiao="harmonizacao-facial"', 'class="r-grupo is-ativo" data-regiao="harmonizacao-facial"')
    numeros = ""
    if D.NUMEROS:
        numeros = '<div class="numeros">' + "".join(f"<div><b>{n['valor']}</b><span>{n['rotulo']}</span></div>" for n in D.NUMEROS) + "</div>"
    depoimentos = ""
    if D.DEPOIMENTOS:
        itens = "".join(f"<figure><blockquote>{d['texto']}</blockquote><figcaption>{d['nome']} · {d['tratamento']}</figcaption></figure>" for d in D.DEPOIMENTOS)
        depoimentos = f'<section class="sec sec--branca"><div class="casco"><div class="cabeca revela"><p class="rubrica">Depoimentos</p><h2>Quem já passou pela avaliação</h2></div><div class="depoimentos">{itens}</div></div></section>'
    diferenciais = [
        ("Avaliação individualizada", "O atendimento começa pela análise presencial do rosto, do histórico de saúde e do que você deseja mudar."),
        ("Planejamento personalizado", "O plano parte da sua anatomia e do seu objetivo. Quando mais de um recurso faz sentido, a ordem e o intervalo são definidos caso a caso."),
        ("Transparência sobre indicações e limites", "Você entende o que a técnica faz, o que não faz e quais são os riscos, inclusive quando a melhor resposta é não fazer o procedimento."),
        ("Orientação antes e depois", "Os cuidados prévios e posteriores são explicados conforme o procedimento e o seu caso."),
        ("Acompanhamento", "A evolução é reavaliada depois do procedimento, porque o atendimento não termina ao sair da sala."),
    ]
    lista_dif = "".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a, b in diferenciais)
    corpo = f"""<main id="conteudo">
<section class="heroi">
  <div class="casco heroi__grade">
    <div class="heroi__titulo">
      <p class="rubrica">Estética facial · {D.CRBM}</p>
      <h1><span class="heroi__nome"><span class="heroi__palavra" data-deriva="-1">Elsângela</span> <span class="heroi__palavra" data-deriva="1">Melo</span></span> <span class="heroi__funcao">Biomédica esteta em Goiânia</span></h1>
    </div>
    <figure class="heroi__foto">
      <picture class="paralaxe">
        <source media="(max-width: 899px)" srcset="/assets/img/retrato-globo-amplo-480.webp 480w, /assets/img/retrato-globo-amplo-720.webp 720w, /assets/img/retrato-globo-amplo-959.webp 959w" sizes="calc(100vw - 2.5rem)" width="959" height="682">
        <img src="/assets/img/retrato-globo-546.webp" srcset="/assets/img/retrato-globo-420.webp 420w, /assets/img/retrato-globo-546.webp 546w" sizes="(min-width: 1320px) 480px, 38vw" width="546" height="682" fetchpriority="high" alt="{ALT_GLOBO}">
      </picture>
      <figcaption class="heroi__legenda">{D.CLINICA}, {D.BAIRRO} · {D.CIDADE}, {D.ESTADO}</figcaption>
    </figure>
    <div class="heroi__corpo">
      <p class="chamada">Estética facial com planejamento individual: primeiro entender o seu rosto e o que você deseja; depois explicar o que é indicado e quais são os limites de cada técnica.</p>
      <div class="acoes">
        {btn_wa("Agendar avaliação", D.WA_PADRAO, "home-heroi")}
        <a class="btn btn--fio" href="#tratamentos">Conhecer os tratamentos</a>
      </div>
      {numeros}
      <div class="heroi__dados">
        <p><strong>Onde:</strong> {D.CLINICA}, {D.RUA}, {D.BAIRRO}, {D.CIDADE}</p>
        <p><strong>Quando:</strong> {D.HORARIO_CURTO}</p>
        <p><strong>Avaliação:</strong> gratuita</p>
      </div>
    </div>
  </div>
</section>

<section class="sec sec--branca fio-topo" id="tratamentos">
  <div class="casco">
    <div class="cabeca revela">
      <p class="rubrica">Tratamentos</p>
      <h2>Oito recursos, <em>um rosto de cada vez</em></h2>
      <p class="chamada">Cada recurso atua em uma região ou camada diferente. Percorra o mapa para entender o que cada um faz. A indicação é sempre definida na avaliação presencial.</p>
    </div>
    <div class="mapa" data-mapa-rosto>
      <div class="mapa__figura revela">
        {grupos}
        <p class="mapa__legenda" data-mapa-legenda><b>{D.TRATAMENTOS[0]['nome']}</b><span>Referência: {F.ROTULOS[D.TRATAMENTOS[0]['slug']]}.</span></p>
      </div>
      <div class="mapa__linhas">{''.join(linhas)}
        <p style="margin-top:2rem">{seta("Ver a página completa de tratamentos", "/tratamentos/")}</p>
      </div>
    </div>
  </div>
</section>

<div class="faixa" aria-hidden="true"><div class="faixa__texto" data-faixa><span data-t="Avaliação"></span><i data-t="planejamento"></i><span data-t="Proporção"></span><i data-t="cuidado"></i><span data-t="Acompanhamento"></span><i data-t="critério"></i><span data-t="Avaliação"></span><i data-t="planejamento"></i></div></div>

<section class="sec">
  <div class="casco sobre">
    <div class="sobre__foto paralaxe revela">{foto_oculos("(min-width: 900px) 480px, 90vw")}</div>
    <div class="sobre__texto revela">
      <p class="rubrica">Sobre a profissional</p>
      <h2>{D.NOME}</h2>
      <p class="sobre__registro">Biomédica esteta · {D.CRBM}</p>
      <p>{D.NOME} é formada como biomédica esteta e atua com estética facial em Goiânia, na {D.CLINICA}, no {D.BAIRRO}. O atendimento parte de uma avaliação presencial e gratuita: entender o rosto, o histórico de saúde e o objetivo de quem chega, antes de falar em procedimento.</p>
      <p>O que orienta o trabalho é a ideia de que um bom resultado não chama atenção para si. Ele busca equilíbrio e proporção sem apagar os traços que fazem cada pessoa ser reconhecida.</p>
      <div>{seta("Conhecer a profissional", "/sobre/")}</div>
    </div>
  </div>
</section>

<section class="sec sec--rosado">
  <div class="casco duas-colunas">
    <div class="duas-colunas__fixa cabeca revela" style="margin:0">
      <p class="rubrica">Como o atendimento é conduzido</p>
      <h2>Critério antes <em>de qualquer técnica</em></h2>
    </div>
    <ul class="lista-fio" data-cascata>{lista_dif}</ul>
  </div>
</section>

{secao_passos()}

<section class="palco fio-topo" data-palco>
  <div class="palco__fixo"><div class="casco">
    <p class="rubrica">O que esperar</p>
    <h2 class="frase">{palavras("Um bom resultado <em>não chama atenção</em> para si.")}</h2>
  </div></div>
</section>
<section class="pos-palco"><div class="casco">
  <div class="fatores" data-cascata>
    <div><h3>Cada rosto responde de um jeito</h3><p>Anatomia, resposta do organismo, hábitos e cuidados depois do procedimento influenciam o que se vê. Os resultados variam de pessoa para pessoa.</p></div>
    <div><h3>A expectativa vem antes</h3><p>A avaliação serve para separar o que a técnica faz do que ela não faz. Se o objetivo não for compatível com a indicação, isso é dito antes.</p></div>
    <div><h3>Resultados no Instagram</h3><p>Os registros do trabalho ficam no Instagram. Aqui no site, você entende o que influencia cada resultado.</p>{seta("Ver no Instagram " + D.INSTAGRAM_H, D.INSTAGRAM, ' rel="noopener" data-origem="home-resultados"')}{seta("O que influencia um resultado", "/resultados/")}</div>
  </div>
</div></section>
{depoimentos}
<section class="sec sec--rosado" id="perguntas">
  <div class="casco duas-colunas">
    <div class="duas-colunas__fixa cabeca revela" style="margin:0">
      <p class="rubrica">Informações</p>
      <h2>Perguntas frequentes</h2>
    </div>
    <div class="faq" data-cascata>{faq}</div>
  </div>
</section>

<section class="sec" id="localizacao">
  <div class="casco">
    <div class="cabeca revela"><p class="rubrica">Localização</p><h2>Onde a Elsângela <em>atende</em></h2></div>
    <div class="local">
      <div class="local__dados revela">
        <div><h3>Endereço</h3><address>{D.CLINICA}<br>{D.RUA} — {D.BAIRRO}<br>{D.CIDADE} - {D.UF}, {D.CEP}</address></div>
        <div><h3>Horário de atendimento</h3><p>Segunda a sexta, das 9h às 19h<br>Sábado, das 9h às 14h</p></div>
        <div><h3>WhatsApp e telefone</h3><p><a href="tel:{D.TEL_E164}">{D.TEL}</a></p></div>
        <div class="acoes"><a class="btn btn--fio" href="{D.MAPS}" rel="noopener">Como chegar</a></div>
        <p>{seta("Ver o perfil e as avaliações no Google", D.MAPS, ' rel="noopener"')}</p>
      </div>
      {bloco_mapa_google()}
    </div>
  </div>
</section>

{secao_form()}
</main>"""
    data = data_pagina(url, hash_de(puro(corpo)))
    ld = [ld_site(), ld_pessoa(), ld_clinica(), ld_pagina(url, title, desc, data=data, sobre={"@id": ID_PESSOA}), ld_faq(faq)]
    preload = ('<link rel="preload" as="image" imagesrcset="/assets/img/retrato-globo-amplo-480.webp 480w, /assets/img/retrato-globo-amplo-720.webp 720w, /assets/img/retrato-globo-amplo-959.webp 959w" imagesizes="calc(100vw - 2.5rem)" media="(max-width: 899px)" fetchpriority="high">'
               '<link rel="preload" as="image" imagesrcset="/assets/img/retrato-globo-420.webp 420w, /assets/img/retrato-globo-546.webp 546w" imagesizes="(min-width: 1320px) 480px, 38vw" media="(min-width: 900px)" fetchpriority="high">')
    return documento({"url": url, "title": title, "description": desc, "ld": ld, "preload": preload}, corpo)


def pagina_tratamento(t, artigos):
    s = t["slug"]
    url = f"/{s}/"
    m, corpo, assinatura = fragmento(f"tratamentos/{s}.html")
    corpo, nav = indice(corpo)
    data = data_pagina(url, assinatura + hash_de(json.dumps(t, ensure_ascii=False, sort_keys=True)))
    title = t.get("title", m["title"])
    desc = t.get("description", m["description"])
    h1 = m["h1"].replace(" em Goiânia", " <em>em Goiânia</em>")
    mig = [("Início", "/"), ("Tratamentos", "/tratamentos/"), (t["nome"], url)]
    rel = "".join(ligacao("Tratamento", n["nome"], n["resumo"], f"/{n['slug']}/") for n in D.TRATAMENTOS if n["slug"] in t["rel"])
    art = "".join(ligacao("Artigo", artigos[a]["h1"], artigos[a]["description"], f"/blog/{a}/") for a in t["artigos"])
    msg = D.wa_tratamento(t["minusculo"])
    p = m["procedimento"]
    servico = {
        "@type": "Service", "@id": f"{D.SITE}{url}#servico", "name": t["nome"], "serviceType": t["nome"], "url": f"{D.SITE}{url}", "description": desc,
        "provider": {"@type": "Person", "@id": ID_PESSOA, "name": D.NOME, "jobTitle": D.PROFISSAO, "url": f"{D.SITE}/sobre/"},
        "areaServed": {"@type": "City", "name": D.CIDADE},
    }
    procedimento = {"@type": "MedicalProcedure", "name": p["name"], **{k: p[k] for k in ("alternateName", "bodyLocation", "howPerformed", "preparation", "followup") if p.get(k)}}
    revisao = f" Conteúdo revisado por {D.NOME}, {D.CRBM}." if D.CONTEUDO_REVISADO else ""
    html_corpo = f"""<main id="conteudo">
<section class="pag-heroi">
  <div class="casco">
    {migalhas(mig)}
    <div class="pag-heroi__grade" style="margin-top:1.5rem">
      <div class="pag-heroi__texto">
        <p class="rubrica">Tratamento em estética facial</p>
        <h1>{h1}</h1>
        <p class="chamada">{m['lead']}</p>
        <div class="acoes">
          {btn_wa("Agendar avaliação", msg, f"{s}-heroi")}
          <a class="btn btn--fio" href="/tratamentos/">Ver todos os tratamentos</a>
        </div>
      </div>
      <figure class="pag-heroi__fig">
        <img data-flutua src="{rosto(s)}" width="400" height="520" fetchpriority="high" alt="Ilustração em traço fino do rosto que destaca {esc(F.ROTULOS[s])}">
        <figcaption>Ilustração de referência. A região de cada caso é definida na avaliação.</figcaption>
      </figure>
    </div>
  </div>
</section>
<section class="resposta"><div class="casco"><div class="resposta__texto">{m['resposta']}</div><p class="meta-pag">Atualizado em <time datetime="{data}">{data_br(data)}</time>.{revisao}</p></div></section>
<div class="casco leitura">
  {nav}
  <article class="prosa">
{corpo}
  {aviso()}
  </article>
</div>
<section class="sec sec--curta fio-topo"><div class="casco acoes" style="align-items:center;justify-content:space-between">
  <p class="chamada" style="margin:0">Quer entender se {t['minusculo']} faz sentido para o seu caso?</p>
  {btn_wa("Perguntar no WhatsApp", msg, f"{s}-meio")}
</div></section>
{bloco_profissional()}
<section class="sec sec--curta fio-topo"><div class="casco">
  <div class="cabeca revela"><p class="rubrica">Continue lendo</p><h2>Tratamentos relacionados</h2></div>
  <div class="grade-liga grade-liga--3" data-cascata>{rel}</div>
  <h2 style="margin-block:3.5rem 2rem;font-size:clamp(1.75rem,3vw,2.5rem)">Artigos relacionados</h2>
  <div class="grade-liga grade-liga--3" data-cascata>{art}</div>
</div></section>
{bloco_local()}
{faixa_cta(m['cta'], msg, f"{s}-cta")}
</main>"""
    ld = [ld_pagina(url, title, desc, data=data, sobre=procedimento), ld_migalhas(mig), servico, ld_faq(corpo)]
    return documento({"url": url, "title": title, "description": desc, "ld": ld, "og_tipo": "article", "og_imagem": f"/assets/og/{s}.jpg", "og_alt": f"{t['nome']} em Goiânia, com Elsângela Melo, biomédica esteta"},
                     html_corpo, "/tratamentos/", atributos=f' data-tratamento="{s}"')


def pagina_artigo(a, artigos):
    url = f"/blog/{a}/"
    d = artigos[a]
    corpo, nav = indice(d["corpo"])
    data = data_pagina(url, d["assinatura"] + hash_de(json.dumps(D.ARTIGO_AJUSTES.get(a, {}), ensure_ascii=False)))
    mig = [("Início", "/"), ("Blog", "/blog/"), (d["h1"], url)]
    palavras = len(puro(corpo).split())
    minutos = max(2, round(palavras / 200))
    rel = "".join(ligacao(r["tipo"], r["titulo"], r["resumo"], r["href"]) for r in d["relacionados"])
    msg = D.wa_artigo(d["h1"])
    revisao = f" Conteúdo revisado por {D.NOME}, {D.CRBM}." if D.CONTEUDO_REVISADO else ""
    html_corpo = f"""<main id="conteudo">
<section class="pag-heroi">
  <div class="casco">
    {migalhas(mig)}
    <div class="pag-heroi__texto" style="margin-top:1.5rem;max-width:58rem">
      <p class="rubrica">Blog</p>
      <h1>{d['h1']}</h1>
      <p class="meta-pag" style="margin:0">Publicado por {D.NOME}, biomédica esteta · <time datetime="{d['publicado']}">{data_br(d['publicado'])}</time>{f' · atualizado em <time datetime="{data}">{data_br(data)}</time>' if data != d['publicado'] else ''} · {minutos} min de leitura.{revisao}</p>
    </div>
  </div>
</section>
<section class="resposta"><div class="casco"><div class="resposta__texto">{d['resposta']}</div></div></section>
<div class="casco leitura">
  {nav}
  <article class="prosa">
{corpo}
  {aviso(d['aviso'] or AVISO_PADRAO)}
  </article>
</div>
{bloco_profissional()}
<section class="sec sec--curta fio-topo"><div class="casco">
  <div class="cabeca revela"><p class="rubrica">Leia também</p><h2>Para continuar a leitura</h2></div>
  <div class="grade-liga" data-cascata>{rel}</div>
</div></section>
{faixa_cta(d['cta'], msg, f"blog-{a}")}
</main>"""
    pessoa = {"@type": "Person", "@id": ID_PESSOA, "name": D.NOME, "jobTitle": D.PROFISSAO, "url": f"{D.SITE}/sobre/",
              "identifier": {"@type": "PropertyValue", "name": "CRBM-3", "value": D.CRBM.split()[-1]}}
    artigo = {"@type": "BlogPosting", "@id": f"{D.SITE}{url}#artigo", "headline": d["h1"], "description": d["description"], "inLanguage": "pt-BR",
              "datePublished": d["publicado"], "dateModified": data, "author": pessoa, "publisher": {"@id": ID_PESSOA},
              "mainEntityOfPage": f"{D.SITE}{url}", "image": f"{D.SITE}/og-image.jpg", "url": f"{D.SITE}{url}", "wordCount": palavras}
    if D.CONTEUDO_REVISADO:
        artigo["reviewedBy"] = {"@id": ID_PESSOA}
    ld = [ld_migalhas(mig), artigo, ld_faq(corpo)]
    return documento({"url": url, "title": d["title"], "description": d["description"], "ld": ld, "og_tipo": "article"}, html_corpo, "/blog/")


def pagina_tratamentos():
    url = "/tratamentos/"
    title = "Tratamentos de Estética Facial em Goiânia | Elsângela Melo"
    desc = "Conheça os 8 tratamentos de estética facial realizados por Elsângela Melo, biomédica esteta em Goiânia, e entenda como a avaliação define cada indicação."
    _, faq, _ = fragmento("_faq-tratamentos.html")
    _, texto, _ = fragmento("_tratamentos-texto.html")
    partes = re.split(r"(?=<h2>Sobre valores</h2>)", texto)
    cartoes = "".join(f"""<a class="cartao revela" href="/{t['slug']}/">
        <div class="cartao__fig"><img src="{rosto(t['slug'])}" width="400" height="520" loading="lazy" decoding="async" alt="Ilustração do rosto que destaca {esc(F.ROTULOS[t['slug']])}"></div>
        <h3>{t['nome']}</h3><p>{t['resumo']}</p><p><strong>Pode ser considerado para:</strong> {t['considerar']}.</p></a>""" for t in D.TRATAMENTOS)
    mig = [("Início", "/"), ("Tratamentos", url)]
    corpo = f"""<main id="conteudo">
<section class="pag-heroi"><div class="casco">
  {migalhas(mig)}
  <div class="pag-heroi__texto" style="margin-top:1.5rem;max-width:62rem">
    <p class="rubrica">Tratamentos</p>
    <h1>Tratamentos de estética facial <em>em Goiânia</em></h1>
    <p class="chamada">Oito recursos realizados por Elsângela Melo, biomédica esteta, na {D.CLINICA}. Cada um atende a um objetivo diferente, e a indicação sempre nasce de uma avaliação individual.</p>
    <div class="acoes">{btn_wa("Agendar avaliação", "Olá! Acessei o site da Elsângela Melo e gostaria de informações sobre uma avaliação para entender qual tratamento é indicado para mim.", "tratamentos-heroi")}<a class="btn btn--fio" href="#avaliacao">Como funciona a avaliação</a></div>
  </div>
</div></section>
<section class="resposta"><div class="casco"><div class="resposta__texto"><p><strong>São oito os tratamentos de estética facial oferecidos por Elsângela Melo em Goiânia:</strong> harmonização facial, preenchimento labial, toxina botulínica, bioestimuladores de colágeno, skinbooster, peeling, microagulhamento e limpeza de pele. A avaliação é gratuita.</p></div></div></section>
<section class="sec"><div class="casco">
  <div class="prosa" style="margin-bottom:clamp(2.5rem,6vw,5rem)">
    <p>A <strong>harmonização facial</strong> é um planejamento que pode combinar mais de um recurso. <strong>Preenchimento labial, toxina botulínica, bioestimuladores e skinbooster</strong> são injetáveis, com profundidades e propósitos distintos. <strong>Peeling e microagulhamento</strong> trabalham a textura, o tom e a resposta da própria pele. A <strong>limpeza de pele</strong> cuida da remoção de impurezas e do excesso de oleosidade. Conhecer a diferença ajuda a chegar à avaliação com perguntas melhores.</p>
  </div>
  <div class="cabeca revela"><p class="rubrica">Os oito recursos</p><h2>Escolha um tratamento <em>para entender melhor</em></h2></div>
  <div class="cartoes">{cartoes}</div>
</div></section>
<section class="sec sec--rosado"><div class="casco"><div class="prosa">{partes[0]}</div></div></section>
{secao_passos()}
<section class="sec sec--branca fio-topo"><div class="casco"><div class="prosa">{partes[1] if len(partes) > 1 else ''}</div></div></section>
<section class="sec"><div class="casco duas-colunas">
  <div class="duas-colunas__fixa cabeca" style="margin:0"><p class="rubrica">Informações</p><h2>Perguntas frequentes</h2></div>
  <div><div class="faq">{faq}</div>{aviso()}</div>
</div></section>
{faixa_cta("Antes de escolher entre um tratamento e outro, vale entender o que é indicado para o seu rosto. A avaliação em Goiânia começa por aí.", "Olá! Acessei o site da Elsângela Melo e gostaria de informações sobre uma avaliação para entender qual tratamento é indicado para mim.", "tratamentos-cta")}
</main>"""
    data = data_pagina(url, hash_de(puro(corpo)))
    lista = {"@type": "ItemList", "name": "Tratamentos de estética facial", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": t["nome"], "url": f"{D.SITE}/{t['slug']}/"} for i, t in enumerate(D.TRATAMENTOS)]}
    ld = [ld_pagina(url, title, desc, "CollectionPage", data), ld_migalhas(mig), lista, ld_faq(faq)]
    return documento({"url": url, "title": title, "description": desc, "ld": ld}, corpo, url)


def pagina_sobre():
    url = "/sobre/"
    title = "Sobre Elsângela Melo | Biomédica Esteta em Goiânia"
    desc = "Elsângela Melo é biomédica esteta em Goiânia, CRBM-3 17215, e atua com estética facial na MaBelly Aesthetics, no Setor Coimbra. Conheça a forma de trabalhar."
    mig = [("Início", "/"), ("Sobre", url)]
    principios = [
        ("Naturalidade como critério", "O objetivo não é transformar um rosto em outro. É trabalhar dentro da anatomia que já existe, respeitando volume, proporção e movimento."),
        ("Avaliação individualizada", "Não existe protocolo aplicado igualmente a todas as pessoas. A avaliação presencial analisa estrutura, qualidade da pele, mímica, histórico de saúde e o que incomoda, e só então define o que é indicado."),
        ("Respeito à identidade e à expressão", "Traços que identificam alguém não são defeitos a corrigir. A conduta procura preservar a capacidade de expressar emoção."),
        ("Rigor técnico e segurança", "Produtos regularizados junto à ANVISA, técnica dentro dos limites da formação profissional e conduta clara diante de qualquer intercorrência. Quando um caso pede outra especialidade, o encaminhamento é feito."),
        ("Expectativa alinhada antes de começar", "A conversa anterior ao procedimento explica o que a técnica faz, o que não faz e como é a recuperação. Se a expectativa não for compatível, isso é dito antes, e o procedimento pode não ser indicado."),
        ("Acompanhamento depois", "Orientações de cuidado e retorno para avaliar como o rosto respondeu fazem parte do mesmo processo."),
    ]
    lista_p = "".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a, b in principios)
    linha_numeros = "".join(f"<div><dt>{n['rotulo'].capitalize()}</dt><dd>{n['valor']}</dd></div>" for n in D.NUMEROS)
    bio = "".join(f"<p>{p}</p>" for p in D.BIOGRAFIA)
    formacao = ""
    if D.FORMACAO:
        itens = "".join(f"<li><b>{f.get('ano', '')}</b><div><strong>{f['curso']}</strong><br>{f.get('instituicao', '')}{' · ' + f['tipo'] if f.get('tipo') else ''}</div></li>" for f in D.FORMACAO)
        formacao = f'<section class="sec sec--rosado"><div class="casco"><div class="cabeca revela"><p class="rubrica">Qualificação</p><h2>Formação e certificações</h2></div><ul class="linha-tempo">{itens}</ul></div></section>'
    trajetoria = ""
    if D.TRAJETORIA:
        itens = "".join(f"<li><b>{f['ano']}</b><div><strong>{f['titulo']}</strong><br>{f.get('texto', '')}</div></li>" for f in D.TRAJETORIA)
        trajetoria = f'<section class="sec"><div class="casco"><div class="cabeca revela"><p class="rubrica">Trajetória</p><h2>Linha do tempo</h2></div><ul class="linha-tempo">{itens}</ul></div></section>'
    corpo = f"""<main id="conteudo">
<section class="pag-heroi"><div class="casco">
  {migalhas(mig)}
  <div class="pag-heroi__grade" style="margin-top:1.5rem;align-items:center">
    <div class="pag-heroi__texto">
      <p class="rubrica">Sobre a profissional</p>
      <h1>Sobre <em>Elsângela Melo</em></h1>
      <p class="chamada">Biomédica esteta em Goiânia, com atuação em estética facial e atendimento na {D.CLINICA}, no {D.BAIRRO}. Uma prática construída sobre avaliação individual, técnica cuidadosa e respeito à expressão de cada rosto.</p>
      <div class="acoes">{btn_wa("Agendar avaliação", D.WA_PADRAO, "sobre-heroi")}<a class="btn btn--fio" href="/tratamentos/">Ver tratamentos</a></div>
    </div>
    <div class="pag-heroi__foto paralaxe">{foto_oculos("(min-width: 900px) 30vw, 90vw", lazy=False)}</div>
  </div>
</div></section>
<section class="resposta"><div class="casco"><div class="resposta__texto"><p><strong>Elsângela Melo é formada como biomédica esteta, com registro {D.CRBM} (Conselho Regional de Biomedicina da 3ª Região), e atua com estética facial em Goiânia, Goiás.</strong> O atendimento é realizado na {D.CLINICA}, na {D.RUA}, {D.BAIRRO}.</p></div></div></section>
<section class="sec"><div class="casco"><div class="prosa">
  <h2>Apresentação</h2>
  <p>A prática de Elsângela Melo é dedicada à estética facial, um campo que exige duas coisas ao mesmo tempo: conhecimento técnico da anatomia e da fisiologia do rosto e uma leitura atenta de quem chega ao atendimento.</p>
  <p>O que orienta o trabalho é a ideia de que um bom resultado não chama atenção para si. Ele busca equilíbrio e proporção sem apagar os traços pelos quais cada pessoa é reconhecida. Cada plano é construído a partir da avaliação presencial, com o que é indicado para aquele rosto e para aquele momento.</p>
  {bio}
</div></div></section>
{formacao}
{trajetoria}
<section class="sec sec--rosado"><div class="casco duas-colunas">
  <div class="duas-colunas__fixa cabeca" style="margin:0"><p class="rubrica">Filosofia de atendimento</p><h2>Como se trabalha <em>aqui</em></h2></div>
  <ul class="lista-fio" data-cascata>{lista_p}</ul>
</div></section>
<section class="sec"><div class="casco duas-colunas">
  <div class="duas-colunas__fixa cabeca" style="margin:0"><p class="rubrica">Transparência</p><h2>Registro e dados profissionais</h2><p class="chamada">Dados informados nos canais oficiais, para conferência antes do agendamento.</p></div>
  <dl class="tabela-dados">
    <div><dt>Nome</dt><dd>{D.NOME}</dd></div>
    <div><dt>Profissão</dt><dd>{D.PROFISSAO}</dd></div>
    <div><dt>Registro</dt><dd>{D.CRBM}, Conselho Regional de Biomedicina da 3ª Região</dd></div>
    <div><dt>Área de atuação</dt><dd>Estética facial</dd></div>
    {linha_numeros}
    <div><dt>Local</dt><dd>{D.CLINICA}<br>{D.RUA} — {D.BAIRRO}<br>{D.CIDADE} - {D.UF}, {D.CEP}</dd></div>
    <div><dt>Contato</dt><dd><a href="{D.wa()}" rel="noopener">WhatsApp {D.TEL}</a><br><a href="mailto:{D.EMAIL}">{D.EMAIL}</a></dd></div>
    <div><dt>Horário</dt><dd>Segunda a sexta, das 9h às 19h<br>Sábado, das 9h às 14h</dd></div>
  </dl>
</div></section>
<section class="sec sec--curta sec--branca fio-topo"><div class="casco">
  <div class="cabeca revela"><p class="rubrica">Continue conhecendo</p><h2>O trabalho em detalhe</h2></div>
  <div class="grade-liga grade-liga--3">
    {ligacao("Tratamentos", "Todos os tratamentos", "Os oito recursos de estética facial e como a avaliação define cada indicação.", "/tratamentos/")}
    {ligacao("Resultados", "O que esperar de um resultado", "Por que os resultados variam e como a expectativa é alinhada.", "/resultados/")}
    {ligacao("Blog", "Artigos sobre estética facial", "Leituras para decidir com informação, sem promessa de resultado.", "/blog/")}
  </div>
  {aviso("O conteúdo desta página é informativo e não substitui a avaliação presencial. A indicação de qualquer procedimento depende de análise individual do rosto, do histórico de saúde e do objetivo de cada pessoa.")}
</div></section>
{faixa_cta("Se você quer entender o que faz sentido para o seu rosto, a avaliação presencial é onde essa conversa começa, sem compromisso de realizar qualquer procedimento no mesmo dia.", D.WA_PADRAO, "sobre-cta")}
</main>"""
    data = data_pagina(url, hash_de(puro(corpo)))
    pag = ld_pagina(url, title, desc, "ProfilePage", data)
    pag["mainEntity"] = {"@id": ID_PESSOA}
    ld = [pag, ld_migalhas(mig), ld_pessoa(), ld_clinica()]
    return documento({"url": url, "title": title, "description": desc, "ld": ld, "og_tipo": "profile"}, corpo, url)


def pagina_resultados():
    url = "/resultados/"
    title = "Resultados em estética facial: o que esperar | Elsângela Melo"
    desc = "Por que os resultados em estética facial variam de pessoa para pessoa, como a expectativa é alinhada na avaliação e onde ver os registros no Instagram."
    mig = [("Início", "/"), ("Resultados", url)]
    fatores = [
        ("Características individuais e anatomia", "Estrutura óssea, distribuição dos compartimentos de gordura, espessura e elasticidade da pele, força e padrão da musculatura da mímica e simetria de base mudam de rosto para rosto. Definem o que é possível, o que é indicado e o que seria excessivo."),
        ("Resposta biológica", "A velocidade de metabolização de um produto, a resposta do tecido, a intensidade do edema nos primeiros dias e o tempo até a estabilização variam com idade, genética, hábitos, sono, exposição solar, tabagismo e condições de saúde."),
        ("Adesão aos cuidados", "Boa parte do que se vê ao final depende do que acontece fora do atendimento: seguir as orientações do pós-procedimento, manter a fotoproteção diária, cuidar da pele com constância e comparecer aos retornos."),
        ("Expectativa alinhada na avaliação", "A avaliação presencial separa o que a técnica faz do que ela não faz. É nela que se define o objetivo, as etapas, o acompanhamento e o que está fora do alcance daquele procedimento."),
    ]
    lista_f = "".join(f"<li><h3>{a}</h3><p>{b}</p></li>" for a, b in fatores)
    corpo = f"""<main id="conteudo">
<section class="pag-heroi"><div class="casco">
  {migalhas(mig)}
  <div class="pag-heroi__texto" style="margin-top:1.5rem;max-width:62rem">
    <p class="rubrica">Resultados</p>
    <h1>O que esperar <em>de um resultado</em></h1>
    <p class="chamada">Duas pessoas podem receber a mesma técnica, na mesma região, com o mesmo produto, e chegar a desfechos diferentes. Entender de onde vem essa variação ajuda a formar uma expectativa realista antes de qualquer decisão.</p>
    <div class="acoes"><a class="btn" data-origem="resultados-heroi" href="{D.INSTAGRAM}" rel="noopener">Ver resultados no Instagram</a>{btn_wa("Agendar avaliação gratuita", D.WA_PADRAO, "resultados-heroi", "btn btn--fio")}</div>
  </div>
</div></section>
<section class="resposta"><div class="casco"><div class="resposta__texto"><p><strong>Os resultados em estética facial variam de acordo com as características individuais, a avaliação e a resposta de cada pessoa.</strong> Nenhum registro de outra pessoa deve ser lido como previsão do seu resultado.</p></div></div></section>
<section class="sec"><div class="casco duas-colunas">
  <div class="duas-colunas__fixa cabeca" style="margin:0"><p class="rubrica">O que influencia</p><h2>Por que os resultados <em>variam</em></h2></div>
  <ul class="lista-fio" data-cascata>{lista_f}</ul>
</div></section>
<section class="sec sec--rosado"><div class="casco duas-colunas">
  <div class="duas-colunas__fixa cabeca" style="margin:0"><p class="rubrica">Registros do trabalho</p><h2>Os resultados ficam <em>no Instagram</em></h2></div>
  <div class="prosa">
    <p>Este site não publica fotos de antes e depois. Para ver registros do trabalho, acesse <a href="{D.INSTAGRAM}" rel="noopener" data-origem="resultados-texto">{D.INSTAGRAM_H}</a> no Instagram.</p>
    <p>Cada registro mostra o que aconteceu com uma pessoa específica, com um plano feito para ela. Por isso, não deve ser lido como previsão do seu resultado.</p>
    <p>As ilustrações em traço fino deste site servem apenas para indicar regiões do rosto de forma educativa. Para saber mais sobre cada técnica, leia os <a href="/blog/">artigos do blog</a>.</p>
    <p><a class="btn" data-origem="resultados-secao" href="{D.INSTAGRAM}" rel="noopener">Ver resultados no Instagram</a></p>
  </div>
</div></section>
<section class="sec sec--curta"><div class="casco">
  <div class="cabeca revela"><p class="rubrica">Tratamentos</p><h2>Entenda cada técnica</h2></div>
  <div class="grade-liga grade-liga--3">{''.join(ligacao("Tratamento", t['nome'], t['resumo'], f"/{t['slug']}/") for t in D.TRATAMENTOS[:3])}</div>
  {aviso("O conteúdo desta página é informativo e não substitui a avaliação presencial. A indicação de qualquer procedimento depende da análise individual do rosto, do histórico de saúde e do objetivo de cada pessoa.")}
</div></section>
{faixa_cta("Antes de olhar o resultado de outra pessoa, vale entender o que é indicado para o seu rosto. Isso só a avaliação presencial responde.", D.WA_PADRAO, "resultados-cta")}
</main>"""
    data = data_pagina(url, hash_de(puro(corpo)))
    ld = [ld_pagina(url, title, desc, data=data), ld_migalhas(mig)]
    return documento({"url": url, "title": title, "description": desc, "ld": ld}, corpo, url)


def pagina_contato():
    url = "/contato/"
    title = "Contato e agendamento em Goiânia | Elsângela Melo"
    desc = "Fale com a biomédica esteta Elsângela Melo em Goiânia: WhatsApp (62) 98202-2330, endereço no Setor Coimbra, horários de atendimento e formulário de avaliação."
    _, faq, _ = fragmento("_faq-contato.html")
    mig = [("Início", "/"), ("Contato", url)]
    corpo = f"""<main id="conteudo">
<section class="pag-heroi"><div class="casco">
  {migalhas(mig)}
  <div class="pag-heroi__texto" style="margin-top:1.5rem;max-width:62rem">
    <p class="rubrica">Contato</p>
    <h1>Contato e agendamento <em>em Goiânia</em></h1>
    <p class="chamada">A avaliação é gratuita, e o agendamento é feito pelo WhatsApp. Você pode escrever direto ou preencher o formulário desta página, que abre a conversa com a mensagem pronta.</p>
    <div class="acoes">{btn_wa("Falar no WhatsApp", D.WA_PADRAO, "contato-heroi")}<a class="btn btn--fio" href="#formulario">Preencher o formulário</a></div>
  </div>
</div></section>
<section class="resposta"><div class="casco"><div class="resposta__texto">
  <p><strong>Onde fica:</strong> {D.CLINICA}, {D.ENDERECO_LINHA}.</p>
  <p><strong>Quando:</strong> segunda a sexta, das 9h às 19h; sábado, das 9h às 14h.</p>
</div></div></section>
<section class="sec" id="localizacao"><div class="casco local">
  <div>
    <div class="cabeca revela"><p class="rubrica">Dados de atendimento</p><h2>Onde encontrar</h2></div>
    <dl class="tabela-dados">
      <div><dt>Profissional</dt><dd>{D.NOME}, {D.PROFISSAO.lower()}</dd></div>
      <div><dt>Registro</dt><dd>{D.CRBM}</dd></div>
      <div><dt>Clínica</dt><dd>{D.CLINICA}</dd></div>
      <div><dt>Endereço</dt><dd>{D.RUA} — {D.BAIRRO}<br>{D.CIDADE} - {D.UF}, {D.CEP}</dd></div>
      <div><dt>WhatsApp e telefone</dt><dd><a href="tel:{D.TEL_E164}">{D.TEL}</a></dd></div>
      <div><dt>Instagram</dt><dd><a href="{D.INSTAGRAM}" rel="noopener">{D.INSTAGRAM_H}</a></dd></div>
      <div><dt>E-mail</dt><dd><a href="mailto:{D.EMAIL}">{D.EMAIL}</a></dd></div>
      <div><dt>Horário</dt><dd>Segunda a sexta, das 9h às 19h<br>Sábado, das 9h às 14h</dd></div>
    </dl>
  </div>
  <div>
    {bloco_mapa_google()}
    <div class="acoes" style="margin-top:1rem"><a class="btn" href="{D.MAPS}" rel="noopener">Como chegar</a><a class="btn btn--fio" href="{D.MAPS}" rel="noopener">Avaliações no Google</a></div>
  </div>
</div></section>
{secao_form(titulo="Solicite <em>uma avaliação</em>", ancora="formulario")}
<section class="sec"><div class="casco duas-colunas">
  <div class="duas-colunas__fixa cabeca" style="margin:0"><p class="rubrica">Informações</p><h2>Perguntas frequentes</h2></div>
  <div><div class="faq">{faq}</div>{aviso("O WhatsApp é um canal de agendamento e de dúvidas gerais. O conteúdo deste site é informativo e não substitui a avaliação presencial.")}</div>
</div></section>
</main>"""
    data = data_pagina(url, hash_de(puro(corpo)))
    ld = [ld_pagina(url, title, desc, "ContactPage", data, {"@id": ID_CLINICA}), ld_migalhas(mig), ld_pessoa(), ld_clinica(), ld_faq(faq)]
    return documento({"url": url, "title": title, "description": desc, "ld": ld}, corpo, url)


def pagina_agendamento():
    url = "/agendamento/"
    title = "Solicitar avaliação | Elsângela Melo"
    desc = "Solicite uma avaliação de estética facial com Elsângela Melo em Goiânia: escolha o tratamento de interesse e a sua preferência de data e período."
    mig = [("Início", "/"), ("Solicitar avaliação", url)]
    corpo = f"""<main id="conteudo">
<section class="pag-heroi"><div class="casco">
  {migalhas(mig)}
  <div class="pag-heroi__texto" style="margin-top:1.5rem;max-width:58rem">
    <p class="rubrica">Agendamento</p>
    <h1>Solicitar <em>avaliação</em></h1>
    <p class="chamada">A avaliação é gratuita. Conte o seu interesse e a sua preferência de data: a mensagem abre no WhatsApp, e o horário é confirmado por lá conforme a agenda.</p>
  </div>
</div></section>
{secao_form(titulo="Sua preferência <em>de atendimento</em>", texto="Atendimento na " + D.CLINICA + ", " + D.BAIRRO + ", em Goiânia. " + D.HORARIO_LONGO, agendamento=True, ancora="formulario")}
</main>"""
    return documento({"url": url, "title": title, "description": desc, "robots": "noindex, follow"}, corpo)


def pagina_blog(artigos):
    url = "/blog/"
    title = "Blog de Estética Facial com Informação Responsável | Elsângela Melo"
    desc = "Artigos sobre estética facial: o que cada recurso faz, o que esperar e como decidir com informação, sem promessa de resultado. Por Elsângela Melo, em Goiânia."
    mig = [("Início", "/"), ("Blog", url)]
    cartoes = "".join(ligacao(f'<time datetime="{artigos[a]["publicado"]}">{data_br(artigos[a]["publicado"])}</time>', artigos[a]["h1"], artigos[a]["description"], f"/blog/{a}/") for a in D.ARTIGOS)
    trat = "".join(ligacao("Tratamento", t["nome"], t["resumo"], f"/{t['slug']}/") for t in D.TRATAMENTOS[:3])
    corpo = f"""<main id="conteudo">
<section class="pag-heroi"><div class="casco">
  {migalhas(mig)}
  <div class="pag-heroi__texto" style="margin-top:1.5rem;max-width:62rem">
    <p class="rubrica">Blog</p>
    <h1>Estética facial, <em>com informação responsável</em></h1>
    <p class="chamada">Leituras sobre como cada recurso funciona, a quem costuma ser indicado, o que é esperado e quais são os limites. A conduta individual só pode ser definida presencialmente, diante do seu rosto e do seu histórico.</p>
  </div>
</div></section>
<section class="sec sec--branca fio-topo sec--curta"><div class="casco">
  <div class="cabeca revela"><p class="rubrica">Artigos</p><h2>Publicações</h2></div>
  <div class="grade-liga" data-cascata>{cartoes}</div>
</div></section>
<section class="sec sec--curta"><div class="casco">
  <div class="cabeca revela"><p class="rubrica">Tratamentos</p><h2>Conheça os tratamentos</h2></div>
  <div class="grade-liga grade-liga--3">{trat}</div>
  <p style="margin-top:2rem">{seta("Ver todos os tratamentos", "/tratamentos/")}</p>
</div></section>
{faixa_cta("Os artigos ajudam a entender. A indicação para o seu caso depende de uma avaliação presencial.", D.WA_PADRAO, "blog-cta")}
</main>"""
    data = data_pagina(url, hash_de(puro(corpo)))
    blog = {"@type": "Blog", "@id": f"{D.SITE}{url}#blog", "name": "Blog de estética facial de Elsângela Melo", "url": f"{D.SITE}{url}", "inLanguage": "pt-BR",
            "publisher": {"@id": ID_PESSOA}, "blogPost": [{"@type": "BlogPosting", "headline": artigos[a]["h1"], "url": f"{D.SITE}/blog/{a}/", "datePublished": artigos[a]["publicado"]} for a in D.ARTIGOS]}
    ld = [ld_pagina(url, title, desc, "CollectionPage", data), ld_migalhas(mig), blog]
    return documento({"url": url, "title": title, "description": desc, "ld": ld}, corpo, url)


def pagina_privacidade():
    url = "/politica-de-privacidade/"
    title = "Política de Privacidade | Elsângela Melo"
    desc = "Como os dados deste site são tratados: o formulário abre o WhatsApp e nada é gravado aqui. Mapa só a pedido, fontes próprias e os seus direitos pela LGPD."
    m, corpo, assinatura = fragmento("privacidade.html")
    if D.CONTROLADOR["razao_social"] and D.CONTROLADOR["cnpj"]:
        corpo = corpo.replace("<!--controlador-->", f"<p>Razão social: {D.CONTROLADOR['razao_social']}. CNPJ: {D.CONTROLADOR['cnpj']}.</p>")
    corpo = corpo.replace("<!--controlador-->", "")
    corpo, nav = indice(corpo)
    mig = [("Início", "/"), ("Política de Privacidade", url)]
    html_corpo = f"""<main id="conteudo">
<section class="pag-heroi"><div class="casco">
  {migalhas(mig)}
  <div class="pag-heroi__texto" style="margin-top:1.5rem;max-width:58rem">
    <p class="rubrica">Privacidade</p>
    <h1>Política de Privacidade</h1>
    <p class="chamada">{m['lead']}</p>
  </div>
</div></section>
<div class="casco leitura fio-topo">
  {nav}
  <article class="prosa">{corpo}</article>
</div>
</main>"""
    data = data_pagina(url, assinatura)
    ld = [ld_pagina(url, title, desc, data=data), ld_migalhas(mig)]
    return documento({"url": url, "title": title, "description": desc, "ld": ld, "robots": "index, follow"}, html_corpo)


def pagina_links():
    url = "/links/"
    title = "Links oficiais | Elsângela Melo"
    desc = "Links oficiais de Elsângela Melo, biomédica esteta em Goiânia: WhatsApp, Instagram, agendamento de avaliação, site e como chegar."

    def item(rot, sub, href, track, forte=False, alvo=False):
        classe = "links__item links__item--forte" if forte else "links__item"
        alvo_html = ' target="_blank" rel="noopener"' if alvo else ""
        return f'<li><a class="{classe}" data-origem="links-{track}" href="{esc(href)}"{alvo_html}><span><b>{rot}</b><small>{sub}</small></span>{SETA}</a></li>'

    corpo = f"""<main id="conteudo" class="links">
  <img class="links__foto" src="/assets/img/avatar-512.webp" width="112" height="112" fetchpriority="high" alt="Retrato de Elsângela Melo, biomédica esteta">
  <div>
    <h1>{D.NOME}</h1>
    <p class="rubrica" style="margin-top:.75rem">Biomédica esteta · {D.CRBM}</p>
    <p class="chamada" style="margin:.75rem auto 0">Estética facial em Goiânia, na {D.CLINICA}, {D.BAIRRO}.</p>
  </div>
  <ul class="links__lista">
    {item("WhatsApp", D.TEL, "/whatsapp", "whatsapp", forte=True, alvo=True)}
    {item("Solicitar avaliação", "Escolha o tratamento e a sua preferência", "/agendamento/", "agendamento")}
    {item("Instagram e resultados", D.INSTAGRAM_H, "/instagram", "instagram", alvo=True)}
    {item("Site oficial", "Tratamentos, artigos e contato", "/", "site")}
    {item("Como chegar", f"{D.RUA}, {D.BAIRRO}", D.MAPS, "mapa", alvo=True)}
    {item("Ligar", D.TEL, f"tel:{D.TEL_E164}", "telefone")}
    <li><button class="links__item" type="button" data-copiar="{D.TEL}"><span><b>Copiar telefone</b><small>{D.TEL}</small></span></button></li>
  </ul>
  <p class="links__nota">{D.HORARIO_CURTO}<br><a href="/politica-de-privacidade/">Política de Privacidade</a></p>
</main>"""
    return documento({"url": url, "title": title, "description": desc, "robots": "noindex, follow"}, corpo, sem_moldura=True)


def pagina_404():
    corpo = f"""<main id="conteudo">
<section class="pag-heroi" style="padding-block:clamp(3rem,8vw,7rem)"><div class="casco">
  <div class="pag-heroi__texto" style="max-width:52rem">
    <p class="rubrica">Erro 404</p>
    <h1>Não encontramos <em>essa página</em></h1>
    <p class="chamada">O endereço pode ter mudado ou não existir mais. Os caminhos abaixo levam ao que costuma ser procurado.</p>
    <div class="acoes"><a class="btn" href="/">Ir para o início</a>{btn_wa("Falar no WhatsApp", "Olá! Acessei o site da Elsângela Melo, cheguei por um link que não abriu e gostaria de ajuda.", "404", "btn btn--fio")}</div>
  </div>
</div></section>
<section class="sec sec--curta sec--branca fio-topo"><div class="casco">
  <div class="cabeca"><h2>Talvez você estivesse procurando</h2></div>
  <div class="grade-liga grade-liga--3">
    {ligacao("Tratamentos", "Todos os tratamentos", "Os oito recursos de estética facial.", "/tratamentos/")}
    {ligacao("Profissional", "Sobre Elsângela Melo", "Registro, atuação e forma de trabalhar.", "/sobre/")}
    {ligacao("Contato", "Contato e agendamento", "WhatsApp, endereço e horários.", "/contato/")}
  </div>
</div></section>
</main>"""
    return documento({"url": "/404.html", "title": "Página não encontrada | Elsângela Melo",
                      "description": "A página procurada não existe mais ou mudou de endereço. Veja os tratamentos ou fale pelo WhatsApp.", "robots": "noindex, follow", "canonical": False}, corpo)


# ─── Sitemap e robots ────────────────────────────────────────────────────────
def gerar_sitemap(urls):
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    imagens = {"/": "/assets/img/retrato-globo-546.webp", "/sobre/": "/assets/img/retrato-oculos-682.webp"}
    for u in urls:
        img = f'<image:image><image:loc>{D.SITE}{imagens[u]}</image:loc></image:image>' if u in imagens else ""
        linhas.append(f'  <url><loc>{D.SITE}{u}</loc><lastmod>{DATAS[u]["data"]}</lastmod>{img}</url>')
    linhas.append("</urlset>\n")
    return "\n".join(linhas)


ROBOTS = f"""# elsangelamelo.com
# Nada é bloqueado aqui: CSS, JS e imagens precisam estar acessíveis para os buscadores.
# Páginas sem valor de busca usam <meta name="robots" content="noindex">, não este arquivo.
# Atenção: se o painel do Cloudflare estiver com o robots.txt gerenciado, ele insere
# outro bloco antes deste, com regras para rastreadores de IA. Esse bloco não vem daqui.

User-agent: *
Allow: /

Sitemap: {D.SITE}/sitemap.xml
"""


def gravar(url, conteudo):
    destino = RAIZ / "404.html" if url == "/404.html" else RAIZ / url.strip("/") / "index.html"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(conteudo, encoding="utf-8")


def main():
    global CSS, JS, V_ROSTO, LENIS
    CSS, JS, V_ROSTO, LENIS = publicar_assets()

    artigos = {}
    for a in D.ARTIGOS:
        m, corpo, assinatura = fragmento(f"blog/{a}.html")
        artigos[a] = {**m, **D.ARTIGO_AJUSTES.get(a, {}), "corpo": corpo, "assinatura": assinatura}

    paginas = {
        "/": pagina_home(),
        "/tratamentos/": pagina_tratamentos(),
        "/sobre/": pagina_sobre(),
        "/resultados/": pagina_resultados(),
        "/blog/": pagina_blog(artigos),
        "/contato/": pagina_contato(),
        "/politica-de-privacidade/": pagina_privacidade(),
    }
    for t in D.TRATAMENTOS:
        paginas[f"/{t['slug']}/"] = pagina_tratamento(t, artigos)
    for a in D.ARTIGOS:
        paginas[f"/blog/{a}/"] = pagina_artigo(a, artigos)
    indexaveis = list(paginas)
    paginas["/agendamento/"] = pagina_agendamento()
    paginas["/links/"] = pagina_links()
    paginas["/404.html"] = pagina_404()

    for url, conteudo in paginas.items():
        gravar(url, conteudo)

    (RAIZ / "sitemap.xml").write_text(gerar_sitemap(indexaveis), encoding="utf-8")
    (RAIZ / "robots.txt").write_text(ROBOTS, encoding="utf-8")
    ARQ_DATAS.write_text(json.dumps(DATAS, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    # Arquivos que deixaram de existir: bundle antigo, sem referência, e duplicatas.
    for velho in ["assets/index-BRIcK_zu.css", "assets/index-BrnGiOPD.js", "assets/site.css", "assets/site.js", "placeholder.svg",
                  "assets/hero-portrait-12956966.webp", "assets/about-portrait-new-Bo3ebTWm.webp", "assets/elsangela-avatar.webp"]:
        (RAIZ / velho).unlink(missing_ok=True)
    for pasta in ["whatsapp", "instagram"]:  # o nginx já responde 302 antes de chegar nestes arquivos
        shutil.rmtree(RAIZ / pasta, ignore_errors=True)
    print(f"{len(paginas)} páginas geradas, {len(indexaveis)} no sitemap. CSS {CSS} · JS {JS}")


if __name__ == "__main__":
    main()
