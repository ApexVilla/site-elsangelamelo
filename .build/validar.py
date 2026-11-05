#!/usr/bin/env python3
"""Validação estática do site gerado. Sai com código 1 se houver erro."""
import json, pathlib, re, sys, xml.etree.ElementTree as ET
from html.parser import HTMLParser
RAIZ = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://elsangelamelo.com"
PROIBIDO = [r"\[INSERIR", r"\[inserir", r"lorem ipsum", r"\+500", r"\+6\s*anos", r"6 anos", r"fonts\.googleapis", r"fonts\.gstatic",
            r"Revisado por", r"Aguardando publicação", r"em preenchimento", r"Limpeza de Pele", r"resultados naturais", r"Falar com a equipe", r"viço radiante", r"data-pendente"]
erros, avisos = [], []
class P(HTMLParser):
    def __init__(s):
        super().__init__(); s.t = ""; s.it = False; s.h = []; s.links = []; s.imgs = []; s.ids = set(); s.meta = {}; s.canon = None; s.ld = []; s.inl = False; s.buf = ""; s.scripts = []; s.ext = 0; s.texto = []; s.skip = 0; s.corrente = None; s.bh = ""
    def handle_starttag(s, tag, a):
        a = dict(a)
        if a.get("id"): s.ids.add(a["id"])
        if tag == "title": s.it = True
        if tag == "meta" and (a.get("name") or a.get("property")): s.meta[a.get("name") or a.get("property")] = a.get("content", "")
        if tag == "link":
            if a.get("rel") == "canonical": s.canon = a.get("href")
            elif a.get("href"): s.links.append(a["href"])
            for parte in (a.get("imagesrcset") or "").split(","):
                if parte.strip(): s.links.append(parte.split()[0])
        if tag == "a" and a.get("href") is not None: s.links.append(a["href"])
        if tag in ("img", "source"):
            if tag == "img": s.imgs.append(a)
            if a.get("src"): s.links.append(a["src"])
            for parte in (a.get("srcset") or "").split(","):
                if parte.strip(): s.links.append(parte.split()[0])
        if tag == "script":
            if a.get("type") == "application/ld+json": s.inl = True; s.buf = ""
            elif a.get("src"): s.scripts.append(a["src"]); s.links.append(a["src"])
            else: s.ext += 1
            s.skip += 1
        if tag == "style": s.skip += 1
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"): s.corrente = tag; s.bh = ""
    def handle_endtag(s, tag):
        if tag == "title": s.it = False
        if tag in ("script", "style"): s.skip -= 1
        if tag == "script" and s.inl:
            s.inl = False; s.ld.append(s.buf)
        if tag == s.corrente: s.h.append((tag, s.bh.strip())); s.corrente = None
    def handle_data(s, d):
        if s.it: s.t += d
        if s.inl: s.buf += d
        if s.corrente: s.bh += d
        if not s.skip: s.texto.append(d)
def arquivo_de(url):
    alvo = url.split("#")[0].split("?")[0]
    p = RAIZ / alvo.lstrip("/")
    return p if p.is_file() else (p / "index.html" if (p / "index.html").is_file() else None)
ATALHOS = {"/whatsapp", "/instagram"}  # respondidos pelo nginx com 302
sitemap = [e.text for e in ET.parse(RAIZ / "sitemap.xml").getroot().iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
paginas = sorted(p for p in RAIZ.rglob("*.html") if ".build" not in p.parts and ".docs" not in p.parts and not p.name.startswith("google"))
titulos, descricoes = {}, {}
for arq in paginas:
    rel = "/" + str(arq.relative_to(RAIZ)).replace("index.html", "")
    x = P(); bruto = arq.read_text(encoding="utf-8"); x.feed(bruto)
    texto = " ".join(x.texto)
    e = lambda m: erros.append(f"{rel}: {m}")
    for pad in PROIBIDO:
        if re.search(pad, bruto, re.I): e(f"texto proibido: {pad}")
    h1 = [h for t, h in x.h if t == "h1"]
    if len(h1) != 1: e(f"{len(h1)} H1")
    nivel = 1
    for t, h in x.h:
        n = int(t[1])
        if n > nivel + 1 and t != "h2": e(f"salto de título: {t} «{h[:40]}» depois de h{nivel}")
        nivel = n
    t = x.t.strip(); d = x.meta.get("description", "")
    if not t: e("sem title")
    if len(t) > 70: avisos.append(f"{rel}: title com {len(t)} caracteres")
    if not 90 <= len(d) <= 175: avisos.append(f"{rel}: description com {len(d)} caracteres")
    if t in titulos: e(f"title repetido em {titulos[t]}")
    if d in descricoes: e(f"description repetida em {descricoes[d]}")
    titulos[t] = rel; descricoes[d] = rel
    robots = x.meta.get("robots", "")
    if rel != "/404.html":
        if x.canon != SITE + rel: e(f"canonical {x.canon}")
    indexavel = "noindex" not in robots
    if indexavel and SITE + rel not in sitemap: e("indexável fora do sitemap")
    if not indexavel and SITE + rel in sitemap: e("noindex dentro do sitemap")
    if x.ext: e(f"{x.ext} script inline executável (a CSP bloqueia)")
    for s in x.scripts:
        if s.startswith("http"): e(f"script externo {s}")
    for l in x.links:
        if not l or l == "#": e("link vazio"); continue
        if l.startswith("#"):
            if l[1:] not in x.ids: e(f"âncora inexistente {l}")
        elif l.startswith("/") and l.split("?")[0].rstrip("/") not in ATALHOS:
            destino = arquivo_de(l)
            if not destino: e(f"link interno quebrado {l}")
            elif "#" in l:
                y = P(); y.feed(destino.read_text(encoding="utf-8"))
                if l.split("#")[1] not in y.ids: e(f"âncora inexistente {l}")
            if l.split("#")[0].split("?")[0] and not l.split("#")[0].split("?")[0].endswith("/") and "." not in l.rsplit("/", 1)[-1]: e(f"link sem barra final {l}")
    for i in x.imgs:
        if i.get("alt") is None: e(f"imagem sem alt {i.get('src')}")
        if not (i.get("width") and i.get("height")): e(f"imagem sem dimensões {i.get('src')}")
    for bloco in x.ld:
        try:
            g = json.loads(bloco)
        except Exception as ex:
            e(f"JSON-LD inválido: {ex}"); continue
        for n in g.get("@graph", [g]):
            if n.get("@type") == "FAQPage":
                for q in n["mainEntity"]:
                    if q["name"] not in re.sub(r"\s+", " ", texto): e(f"FAQ fora do conteúdo visível: {q['name'][:50]}")
    img = x.meta.get("og:image", "").replace(SITE, "")
    if img and not arquivo_de(img): e(f"og:image inexistente {img}")
for u in sitemap:
    if not arquivo_de(u.replace(SITE, "")): erros.append(f"sitemap aponta para inexistente: {u}")
print(f"{len(paginas)} páginas · {len(sitemap)} URLs no sitemap")
for a in avisos: print("AVISO", a)
for x in erros: print("ERRO", x)
print("OK" if not erros else f"{len(erros)} ERRO(S)")
sys.exit(1 if erros else 0)
