// Gera ícones e imagens de compartilhamento a partir de HTML, com o Chrome instalado.
// Uso: NODE_PATH=<pasta com playwright-core> node .build/og.mjs   (depois de build.py)
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
const require = createRequire(process.env.PW_DIR ? path.join(process.env.PW_DIR, 'x.js') : import.meta.url);
const { chromium } = require('playwright-core');
const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const url = (p) => 'file://' + path.join(raiz, p);
const TRAT = [['harmonizacao-facial','Harmonização Facial'],['preenchimento-labial','Preenchimento Labial'],['toxina-botulinica','Toxina Botulínica'],['bioestimuladores','Bioestimuladores de Colágeno'],['skinbooster','Skinbooster'],['peeling','Peeling'],['microagulhamento','Microagulhamento']];
const css = `
@font-face{font-family:B;src:url(${url('assets/fonts/bodoni-moda.woff2')});font-weight:400 500}
@font-face{font-family:BI;src:url(${url('assets/fonts/bodoni-moda-italic.woff2')})}
@font-face{font-family:H;src:url(${url('assets/fonts/hanken-grotesk.woff2')});font-weight:300 600}
*{margin:0;box-sizing:border-box}
body{width:1200px;height:630px;background:linear-gradient(135deg,#FBF4F7 0%,#F8F4F1 50%,#FDFCFC 100%);color:#2A1D22;font-family:H;display:grid;grid-template-columns:1fr auto;overflow:hidden}
.t{padding:64px 0 64px 72px;display:flex;flex-direction:column;justify-content:space-between}
.r{font-size:20px;font-weight:500;letter-spacing:.18em;text-transform:uppercase;color:#A2496E}
h1{font-family:B;font-weight:400;font-size:var(--tam,104px);line-height:.98;letter-spacing:-.02em;font-variation-settings:"opsz" 18;margin-top:18px}
.s{font-family:BI;font-size:44px;color:#B3567D;margin-top:18px;font-variation-settings:"opsz" 11}
.p{font-size:24px;color:#746368}
.f{height:630px}
.f img{height:630px;width:auto;display:block}
.fig{padding:36px 56px 0 24px}.fig img{height:594px}
`;
const pag = (tit, sub, img, fig, tam) => `<!doctype html><meta charset=utf-8><style>${css}</style><body><div class=t><div><p class=r>Biomédica esteta · CRBM 17215</p><h1 style="--tam:${tam}px">${tit}</h1><p class=s>${sub}</p></div><p class=p>Mabelly Aesthetics · Setor Coimbra, Goiânia</p></div><div class="f ${fig ? 'fig' : ''}"><img src="${url(img)}"></div>`;
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const c = await b.newContext({ viewport: { width: 1200, height: 630 } });
const p = await c.newPage();
const tmp = path.join(process.env.TMP_OG || '/tmp', 'og-' + process.pid + '.html');
const render = async (html, out) => { fs.writeFileSync(tmp, html); await p.goto('file://' + tmp, { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready); await p.screenshot({ path: path.join(raiz, out), type: 'jpeg', quality: 82 }); };
await render(pag('Elsângela<br>Melo', 'Biomédica esteta em Goiânia', 'assets/img/retrato-globo-546.webp', false, 112), 'og-image.jpg');
fs.mkdirSync(path.join(raiz, 'assets/og'), { recursive: true });
for (const [s, n] of TRAT) await render(pag(n, 'em Goiânia, com Elsângela Melo', `assets/rosto/${s}.svg`, true, n.length > 20 ? 72 : 88), `assets/og/${s}.jpg`);
for (const [tam, out] of [[512, 'favicon.png'], [180, 'apple-touch-icon.png'], [32, '.build/favicon-32.png'], [48, '.build/favicon-48.png']]) {
  const q = await b.newPage({ viewport: { width: tam, height: tam } });
  await q.setContent(`<!doctype html><style>*{margin:0}img{width:${tam}px;height:${tam}px;display:block}</style><img src="data:image/svg+xml;base64,${fs.readFileSync(path.join(raiz, 'favicon.svg')).toString('base64')}">`);
  await q.waitForTimeout(150);
  await q.screenshot({ path: path.join(raiz, out), type: 'png' });
  await q.close();
}
fs.unlinkSync(tmp);
await b.close();
console.log('imagens geradas');
