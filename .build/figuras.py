"""Mapa do rosto: estudo de proporção em traço fino, em SVG.

Ilustração original, sem foto de paciente e sem imagem de banco. As regiões são
referências educativas: quem define a área de cada caso é a avaliação presencial.
"""

CONTORNO = (
    "M200 40C128 40 86 100 82 190C80 250 86 300 104 340C122 382 144 424 172 442"
    "C182 447 192 448 200 448C208 448 218 447 228 442C256 424 278 382 296 340"
    "C314 300 320 250 318 190C314 100 272 40 200 40Z"
)

BASE = f"""
<g class="r-guias" fill="none">
  <path d="M200 6V514" stroke-dasharray="1 6"/>
  <path d="M34 78H366M34 196H366M34 318H366M34 448H366"/>
</g>
<g class="r-cabelo" fill="none">
  <path pathLength="1" d="M200 24C112 20 62 88 62 190C62 280 58 356 30 440M200 24C288 20 338 88 338 190C338 280 342 356 370 440"/>
  <path pathLength="1" d="M200 62C158 72 112 110 90 176M200 62C242 72 288 110 310 176"/>
</g>
<g class="r-traco" fill="none">
  <path class="r-contorno" pathLength="1" d="{CONTORNO}"/>
  <path pathLength="1" d="M146 420C150 454 150 482 126 500C106 512 84 516 62 520M254 420C250 454 250 482 274 500C294 512 316 516 338 520"/>
  <path pathLength="1" d="M118 208C134 190 160 188 182 200M282 208C266 190 240 188 218 200"/>
  <path pathLength="1" d="M128 240C140 224 162 224 176 242C162 248 142 250 128 240ZM272 240C260 224 238 224 224 242C238 248 258 250 272 240Z"/>
  <circle cx="152" cy="236" r="7.5"/><circle cx="248" cy="236" r="7.5"/>
  <path class="r-fino" pathLength="1" d="M132 227C146 215 162 215 174 229M268 227C254 215 238 215 226 229"/>
  <path class="r-fino" pathLength="1" d="M190 246C190 270 186 292 178 306"/>
  <path pathLength="1" d="M176 312C172 320 180 327 188 322C194 328 206 328 212 322C220 327 228 320 224 312"/>
  <path pathLength="1" d="M158 360C172 352 188 344 200 352C212 344 228 352 242 360C226 364 214 366 200 366C186 366 174 364 158 360Z"/>
  <path pathLength="1" d="M158 360C170 386 230 386 242 360"/>
</g>
"""

DEFS = f"""
<defs>
  <pattern id="p-gota" width="13" height="13" patternUnits="userSpaceOnUse"><circle cx="3.5" cy="3.5" r="1.2"/><circle cx="10" cy="10" r=".7"/></pattern>
  <pattern id="p-fio" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(38)"><path d="M0 0V8" stroke-width=".7" stroke="currentColor"/></pattern>
  <pattern id="p-micro" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r=".62"/></pattern>
  <clipPath id="c-rosto"><path d="{CONTORNO}"/></clipPath>
</defs>
"""

PELE = '<g clip-path="url(#c-rosto)" class="r-padrao"><path fill="url(#{p})" d="M60 30H340V460H60Z"/></g>'

REGIOES = {
    "harmonizacao-facial": f"""
      <path class="r-linha" d="{CONTORNO}"/>
      <path class="r-area" d="M92 258C112 244 140 246 158 260C150 282 130 298 104 300C96 288 92 272 92 258ZM308 258C288 244 260 246 242 260C250 282 270 298 296 300C304 288 308 272 308 258Z"/>
      <path class="r-area" d="M170 416C190 426 210 426 230 416C222 432 212 442 200 446C188 442 178 432 170 416Z"/>""",
    "preenchimento-labial": """
      <path class="r-area r-area--forte" d="M158 360C172 352 188 344 200 352C212 344 228 352 242 360C230 386 170 386 158 360Z"/>""",
    "toxina-botulinica": """
      <path class="r-area" d="M128 106C170 88 230 88 272 106C282 128 286 152 284 178C232 162 168 162 116 178C114 152 118 128 128 106Z"/>
      <path class="r-area r-area--forte" d="M186 180C194 177 206 177 214 180L210 224H190Z"/>
      <path class="r-area" d="M88 222C96 214 106 214 116 218L118 250C108 254 96 252 90 246ZM312 222C304 214 294 214 284 218L282 250C292 254 304 252 310 246Z"/>""",
    "bioestimuladores": """
      <path class="r-area" d="M88 256C110 248 138 252 156 266C158 300 148 340 128 382C108 350 92 300 88 256ZM312 256C290 248 262 252 244 266C242 300 252 340 272 382C292 350 308 300 312 256Z"/>""",
    "skinbooster": PELE.format(p="p-gota"),
    "peeling": PELE.format(p="p-fio"),
    "microagulhamento": PELE.format(p="p-micro"),
}

ROTULOS = {
    "harmonizacao-facial": "o rosto como um conjunto: contorno, região das maçãs do rosto e queixo",
    "preenchimento-labial": "a região dos lábios",
    "toxina-botulinica": "o terço superior: testa, região entre as sobrancelhas e lateral dos olhos",
    "bioestimuladores": "as laterais do rosto, nos terços médio e inferior",
    "skinbooster": "a pele do rosto, com pontos que sugerem microaplicações",
    "peeling": "a superfície da pele do rosto, em linhas finas",
    "microagulhamento": "a pele do rosto, em uma trama de pontos muito finos",
}

CSS_ARQUIVO = """
<style>
  svg{{color:{cor}}}
  .r-guias{{stroke:{guia};stroke-width:.7;opacity:.5}}
  .r-cabelo{{stroke:{traco};stroke-width:.8;stroke-linecap:round;opacity:.38}}
  .r-traco{{stroke:{traco};stroke-width:1.15;stroke-linecap:round;stroke-linejoin:round}}
  .r-fino{{stroke-width:.7;opacity:.6}}
  .r-area{{fill:{cor};fill-opacity:.2;stroke:{cor};stroke-width:.9}}
  .r-area--forte{{fill-opacity:.42}}
  .r-linha{{fill:none;stroke:{cor};stroke-width:2.1}}
  .r-padrao{{opacity:.75}}
  pattern circle{{fill:{cor}}}
</style>
"""

PALETA = {"cor": "#B3567D", "guia": "#CAA772", "traco": "#2A1D22"}


def svg_arquivo(slug, paleta=PALETA):
    """SVG autônomo, usado em <img>: um arquivo por tratamento, cacheável."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 520" width="400" height="520">'
        + CSS_ARQUIVO.format(**paleta) + DEFS + REGIOES[slug] + BASE + "</svg>"
    )


def svg_interativo():
    """SVG do mapa da home: todas as regiões, reveladas por CSS conforme a linha ativa."""
    grupos = "".join(f'<g class="r-grupo" data-regiao="{s}">{r}</g>' for s, r in REGIOES.items())
    return (
        '<svg class="rosto" viewBox="0 0 400 520" width="400" height="520" role="img" '
        'aria-label="Estudo de proporção do rosto em traço fino, que destaca a região de cada tratamento.">'
        + DEFS + grupos + BASE + "</svg>"
    )
