// Testes em navegador real. Uso: PW_DIR=<node_modules> BASE=http://127.0.0.1:8198 SAIDA=<pasta> node .build/testes/navegador.mjs
import { createRequire } from 'module';
import fs from 'fs';
import path from 'path';
const req = createRequire(path.join(process.env.PW_DIR, 'x.js'));
const { chromium } = req('playwright-core');
const axeFonte = fs.readFileSync(req.resolve('axe-core/axe.min.js'), 'utf8');
const BASE = process.env.BASE; const SAIDA = process.env.SAIDA;
const PAGINAS = ['/', '/tratamentos/', '/harmonizacao-facial/', '/preenchimento-labial/', '/toxina-botulinica/', '/bioestimuladores/', '/skinbooster/', '/peeling/', '/microagulhamento/', '/sobre/', '/resultados/', '/blog/', '/blog/cuidados-apos-preenchimento-labial/', '/blog/o-que-e-harmonizacao-facial/', '/blog/botox-e-preenchimento-sao-a-mesma-coisa/', '/blog/harmonizacao-facial-pode-ficar-natural/', '/blog/como-escolher-profissional-estetica-facial/', '/contato/', '/agendamento/', '/links/', '/politica-de-privacidade/', '/nao-existe/'];
const LARGURAS = [320, 360, 390, 414, 768, 1024, 1280, 1440, 1920];
const b = await chromium.launch({ executablePath: '/usr/bin/google-chrome', args: ['--no-sandbox'] });
const falhas = []; const ok = (c, m) => { if (!c) falhas.push(m); };
const escutar = (p, rot) => {
  p.on('console', m => { if (m.type() === 'error' && !/404/.test(m.text())) falhas.push(`console ${rot}: ${m.text().slice(0, 180)}`); });
  p.on('pageerror', e => falhas.push(`erro JS ${rot}: ${String(e).slice(0, 180)}`));
};
// 1. Larguras: rolagem lateral e erros
let contagem = 0;
for (const w of LARGURAS) {
  const c = await b.newContext({ viewport: { width: w, height: w < 700 ? 800 : 900 }, hasTouch: w < 1000, isMobile: w < 700 });
  const p = await c.newPage();
  for (const u of PAGINAS) {
    escutar(p, `${u}@${w}`);
    await p.goto(BASE + u, { waitUntil: 'load' });
    const r = await p.evaluate(() => ({ sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth, h1: document.querySelectorAll('h1').length }));
    ok(r.sw <= r.cw, `rolagem lateral ${u} @${w}: ${r.sw}>${r.cw}`);
    ok(r.h1 === 1, `H1 ${u}`);
    p.removeAllListeners('console'); p.removeAllListeners('pageerror');
    contagem++;
  }
  await c.close();
}
console.log(`larguras: ${contagem} combinações de página e largura`);
// 2. Toque (390): alvos < 44px fora de texto corrido
{
  const c = await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true, reducedMotion: 'reduce' });
  const p = await c.newPage();
  for (const u of PAGINAS) {
    await p.goto(BASE + u, { waitUntil: 'load' });
    const peq = await p.evaluate(() => [...document.querySelectorAll('a,button,input,select,textarea,summary')].filter(e => {
      if (!e.offsetParent) return false;
      const r = e.getBoundingClientRect(); if (!r.width) return false;
      if (e.tagName === 'A' && e.closest('p,li,dd,address,.prosa,.faq__body') && !e.matches('.btn,.seta')) return false;
      if (e.type === 'checkbox' || e.type === 'radio') return false;
      return r.height < 44 && r.width < 44 ? true : r.height < 24;
    }).map(e => `${e.tagName} ${(e.textContent || e.name || '').trim().slice(0, 30)} ${Math.round(e.getBoundingClientRect().height)}px`).slice(0, 4));
    ok(!peq.length, `alvo pequeno ${u}: ${peq.join(' | ')}`);
  }
  await c.close();
}
// 3. Acessibilidade (axe, WCAG 2.2 AA), em 390 e 1440, com movimento reduzido
const contagemAxe = {};
for (const [w, h] of [[390, 844], [1440, 900]]) {
  const c = await b.newContext({ viewport: { width: w, height: h }, reducedMotion: 'reduce' });
  const p = await c.newPage();
  for (const u of PAGINAS) {
    await p.goto(BASE + u, { waitUntil: 'load' });
    await p.evaluate(axeFonte);
    const r = await p.evaluate(async () => { const x = await axe.run(document, { runOnly: ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa', 'best-practice'] }); return x.violations.map(v => ({ id: v.id, n: v.nodes.length, alvo: v.nodes[0].target.join(' ').slice(0, 70), resumo: (v.nodes[0].any[0]?.message || v.nodes[0].all[0]?.message || '').slice(0, 110) })); });
    for (const v of r) { const k = `${v.id} @${w}`; contagemAxe[k] = contagemAxe[k] || { paginas: [], ex: `${v.alvo} ${v.resumo}` }; contagemAxe[k].paginas.push(u); }
  }
  await c.close();
}
console.log('axe:', Object.keys(contagemAxe).length ? JSON.stringify(contagemAxe, null, 1) : 'nenhuma violação');
for (const k of Object.keys(contagemAxe)) falhas.push(`axe ${k}`);
// 4. Formulário
{
  const c = await b.newContext({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
  const p = await c.newPage(); escutar(p, 'form');
  await p.addInitScript(() => { window.__abriu = []; window.open = (u) => { window.__abriu.push(u); return null; }; });
  await p.goto(BASE + '/contato/', { waitUntil: 'load' });
  await p.click('[data-form-avaliacao] button[type=submit]');
  ok(await p.getAttribute('#nome', 'aria-invalid') === 'true', 'form: nome vazio deveria ser inválido');
  ok((await p.textContent('#erro-telefone')).length > 5, 'form: sem erro de telefone');
  ok((await p.evaluate(() => document.activeElement.id)) === 'nome', 'form: foco deveria ir ao primeiro erro');
  ok((await p.evaluate(() => window.__abriu.length)) === 0, 'form: não deveria abrir WhatsApp');
  await p.fill('#nome', 'Teste Silva'); await p.fill('#telefone', '123');
  await p.click('[data-form-avaliacao] button[type=submit]');
  ok(await p.getAttribute('#telefone', 'aria-invalid') === 'true', 'form: telefone curto deveria ser inválido');
  await p.fill('#telefone', ''); await p.type('#telefone', '62982022330');
  ok((await p.inputValue('#telefone')) === '(62) 98202-2330', 'form: máscara do telefone: ' + await p.inputValue('#telefone'));
  await p.selectOption('#interesse', 'Peeling'); await p.fill('#mensagem', 'Quero saber sobre sessões');
  const caixa = await p.locator('[name=consentimento]').boundingBox();
  ok(caixa.width <= 26 && caixa.height <= 26, `form: caixa de consentimento deformada ${caixa.width}x${caixa.height}`);
  ok((await p.locator('[name=consentimento]').evaluate(e => getComputedStyle(e).appearance)) !== 'none', 'form: caixa de consentimento sem marca visível');
  await p.check('[name=consentimento]');
  await p.click('[data-form-avaliacao] button[type=submit]');
  const u = await p.evaluate(() => window.__abriu[0] || '');
  const txt = decodeURIComponent(u.split('text=')[1] || '');
  ok(u.startsWith('https://wa.me/5562982022330?text='), 'form: URL do WhatsApp: ' + u.slice(0, 60));
  for (const trecho of ['Teste Silva', '(62) 98202-2330', 'Peeling', 'Quero saber sobre sessões']) ok(txt.includes(trecho), 'form: mensagem sem ' + trecho);
  ok(await p.isVisible('[data-form-status]'), 'form: confirmação não apareceu');
  ok((await p.getAttribute('[data-form-status] a', 'href')) === u, 'form: link alternativo incorreto');
  await p.goto(BASE + '/agendamento/?interesse=skinbooster', { waitUntil: 'load' });
  ok((await p.inputValue('#interesse')) === 'Skinbooster', 'agendamento: interesse pela URL');
  ok(!!(await p.getAttribute('#data', 'min')), 'agendamento: data mínima');
  await c.close(); console.log('formulário: testado');
}
// 5. Mapa só por clique, e sem terceiros antes disso
{
  const c = await b.newContext({ viewport: { width: 1280, height: 900 } });
  const p = await c.newPage(); const externos = [];
  p.on('request', r => { if (!r.url().startsWith(BASE) && !r.url().startsWith('data:')) externos.push(r.url()); });
  const csp = []; p.on('console', m => { if (/Content Security Policy/i.test(m.text())) csp.push(m.text().slice(0, 200)); });
  for (const u of PAGINAS) { await p.goto(BASE + u, { waitUntil: 'networkidle' }); }
  ok(!externos.length, 'requisição a terceiro antes de qualquer ação: ' + externos.slice(0, 3).join(' '));
  await p.goto(BASE + '/contato/', { waitUntil: 'networkidle' });
  await p.click('[data-mapa-google] button');
  await p.waitForSelector('[data-mapa-google] iframe');
  await p.waitForTimeout(2500);
  ok(externos.some(u => u.includes('google.com/maps')), 'mapa: iframe não pediu o Google');
  ok(!csp.length, 'CSP bloqueou algo: ' + csp.join(' | '));
  await p.screenshot({ path: path.join(SAIDA, 'mapa-carregado.jpg'), type: 'jpeg', quality: 60 });
  await c.close(); console.log('mapa: sem terceiros antes do clique; carregou depois; CSP sem bloqueio');
}
// 6. Consentimento: simula um ID só neste teste, sem enviar nada a terceiros
{
  const c = await b.newContext({ viewport: { width: 1280, height: 900 } });
  const p = await c.newPage(); const ga = [];
  await p.route('**/*', async (r) => {
    const u = r.request().url();
    if (u.includes('googletagmanager')) { ga.push(u); return r.abort(); }
    if (r.request().resourceType() === 'document' && u.startsWith(BASE)) { const x = await r.fetch(); const h = { ...x.headers() }; delete h['content-security-policy']; return r.fulfill({ status: x.status(), headers: h, body: (await x.text()).replace('</head>', '<meta name="analytics-id" content="G-TESTE"></head>') }); }
    return r.continue();
  });
  await p.goto(BASE + '/', { waitUntil: 'load' });
  ok(await p.isVisible('.cookies'), 'consentimento: aviso não apareceu');
  ok(!ga.length, 'consentimento: GA carregou antes do aceite');
  await p.click('.cookies button:has-text("Recusar")');
  await p.reload({ waitUntil: 'load' });
  ok(!(await p.isVisible('.cookies')), 'consentimento: aviso voltou após recusa');
  ok(!ga.length, 'consentimento: GA carregou após recusa');
  await p.evaluate(() => localStorage.clear()); await p.reload({ waitUntil: 'load' });
  await p.click('.cookies button:has-text("Aceitar")');
  await p.waitForTimeout(300);
  ok(ga.length === 1, 'consentimento: GA não carregou após aceite');
  await c.close(); console.log('consentimento: aviso, recusa e aceite funcionando (ID simulado só no teste)');
}
// 7. Menu móvel e teclado
{
  const c = await b.newContext({ viewport: { width: 390, height: 844 }, hasTouch: true, isMobile: true });
  const p = await c.newPage(); escutar(p, 'menu');
  await p.goto(BASE + '/', { waitUntil: 'load' });
  ok(!(await p.isVisible('.menu__lista a')), 'menu deveria nascer fechado');
  await p.tap('.menu-botao'); await p.waitForTimeout(350);
  ok(await p.isVisible('.menu__lista a'), 'menu não abriu');
  ok((await p.getAttribute('.menu-botao', 'aria-expanded')) === 'true', 'aria-expanded');
  await p.keyboard.press('Escape'); await p.waitForTimeout(350);
  ok(!(await p.isVisible('.menu__lista a')), 'Esc não fechou o menu');
  await p.tap('.menu-botao'); await p.waitForTimeout(350);
  await p.tap('.menu__lista a[href="/sobre/"]'); await p.waitForURL('**/sobre/');
  await c.close(); console.log('menu: abre, fecha com Esc e navega');
}
// 8. Sem JavaScript e com movimento reduzido: tudo visível e em fluxo normal
{
  const c = await b.newContext({ viewport: { width: 1280, height: 900 }, javaScriptEnabled: false });
  const p = await c.newPage(); await p.goto(BASE + '/', { waitUntil: 'load' });
  ok(await p.isVisible('h1'), 'sem JS: H1 invisível');
  ok((await p.locator('.linha').count()) === 7, 'sem JS: sete tratamentos');
  const vis = await p.locator('.frase').evaluate(e => getComputedStyle(e.querySelector('.palavra')).opacity);
  ok(vis === '1', 'sem JS: frase apagada');
  await c.close();
  const d = await b.newContext({ viewport: { width: 1280, height: 900 }, reducedMotion: 'reduce' });
  const q = await d.newPage(); await q.goto(BASE + '/', { waitUntil: 'load' });
  const r = await q.evaluate(() => ({ c: document.documentElement.className, armados: document.querySelectorAll('.is-armed').length, alt: document.querySelector('.pista')?.style.height, lenis: !!window.Lenis }));
  ok(!r.c.includes('imersivo') && !r.armados && !r.alt && !r.lenis, 'movimento reduzido ainda anima: ' + JSON.stringify(r));
  await d.close(); console.log('sem JS e movimento reduzido: página comum, conteúdo visível');
}
// 9. Rolagem: âncora com rolagem suave e trilho horizontal
{
  const c = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const p = await c.newPage(); escutar(p, 'rolagem');
  await p.goto(BASE + '/peeling/', { waitUntil: 'networkidle' });
  /* Como uma pessoa: rola com a roda do mouse até o índice e só então clica. */
  await p.mouse.move(900, 500);
  for (let i = 0; i < 40; i++) {
    const visivel = await p.evaluate(() => { const r = document.querySelector('.indice a[href="#cuidados-depois"]').getBoundingClientRect(); return r.top > 80 && r.bottom < innerHeight - 20; });
    if (visivel) break;
    await p.mouse.wheel(0, 120); await p.waitForTimeout(120);
  }
  await p.waitForTimeout(700);
  await p.click('.indice a[href="#cuidados-depois"]'); await p.waitForTimeout(2200);
  const top = await p.evaluate(() => Math.round(document.querySelector('#cuidados-depois').getBoundingClientRect().top));
  ok(top >= 40 && top <= 140, `âncora parou em ${top}px do topo`);
  const yFinal = await p.evaluate(() => scrollY);
  await p.mouse.wheel(0, 600); await p.waitForTimeout(1200);
  ok((await p.evaluate(() => scrollY)) > yFinal + 400, 'roda do mouse não rolou depois da âncora');
  await p.goto(BASE + '/', { waitUntil: 'networkidle' });
  const t = await p.evaluate(() => { const s = document.querySelector('[data-pista]'); return { topo: s.getBoundingClientRect().top + scrollY, alt: s.offsetHeight }; });
  await p.evaluate(v => window.scrollTo({ top: v, behavior: 'instant' }), t.topo + (t.alt - 900) * 0.6); await p.waitForTimeout(500);
  const m = await p.evaluate(() => document.querySelector('[data-pista] .passos').style.transform);
  ok(/translate3d\(-\d+/.test(m), 'trilho não andou: ' + m);
  await c.close(); console.log('rolagem: âncora e trilho funcionando');
}
await b.close();
console.log(falhas.length ? `\n${falhas.length} FALHA(S):\n` + [...new Set(falhas)].slice(0, 50).join('\n') : '\nTODOS OS TESTES PASSARAM');
process.exit(falhas.length ? 1 : 0);
