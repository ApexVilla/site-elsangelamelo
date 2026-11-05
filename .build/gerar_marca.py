#!/usr/bin/env python3
"""Desenha o monograma EM a partir dos contornos da fonte Bodoni Moda (vetor, sem depender da fonte)."""
import pathlib
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
RAIZ = pathlib.Path(__file__).resolve().parent.parent
f = instancer.instantiateVariableFont(TTFont(RAIZ / "assets/fonts/bodoni-moda.woff2"), {"opsz": 28, "wght": 400})
gs, cmap = f.getGlyphSet(), f.getBestCmap()
x, trechos, altura = 0, [], f["OS/2"].sCapHeight
for ch in "EM":
    nome = cmap[ord(ch)]
    pen = SVGPathPen(gs, ntos=lambda v: f"{v:.0f}")
    gs[nome].draw(TransformPen(pen, (1, 0, 0, -1, x, altura)))
    trechos.append(pen.getCommands())
    x += gs[nome].width
d = " ".join(trechos)
PADDING = 0.22 * x
lado = x + 2 * PADDING
oy = (lado - altura) / 2
(RAIZ / "assets/icons").mkdir(parents=True, exist_ok=True)
(RAIZ / "assets/icons/em.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {lado:.0f} {lado:.0f}"><g transform="translate({PADDING:.0f} {oy:.0f})"><path fill="#B3567D" d="{d}"/></g></svg>\n')
(RAIZ / "favicon.svg").write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {lado:.0f} {lado:.0f}"><rect width="100%" height="100%" fill="#FDFCFC"/><g transform="translate({PADDING:.0f} {oy:.0f})"><path fill="#B3567D" d="{d}"/></g></svg>\n')
print("marca gerada", int(x), int(altura))
