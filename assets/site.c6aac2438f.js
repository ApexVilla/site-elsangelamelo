(function () {
'use strict';
var doc = document;
var raiz = doc.documentElement;
var scriptAtual = doc.currentScript;
var reduzir = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
var consultaLarga = window.matchMedia('(min-width:1000px)');
var todos = function (seletor, raiz) { return Array.prototype.slice.call((raiz || doc).querySelectorAll(seletor)); };
var botaoMenu = doc.querySelector('.menu-botao');
var menu = doc.getElementById('menu');
if (botaoMenu && menu) {
var definirMenu = function (aberto) {
menu.dataset.aberto = aberto ? 'true' : 'false';
botaoMenu.setAttribute('aria-expanded', aberto ? 'true' : 'false');
botaoMenu.setAttribute('aria-label', aberto ? 'Fechar menu' : 'Abrir menu');
if (aberto) doc.body.dataset.menu = 'aberto'; else delete doc.body.dataset.menu;
};
botaoMenu.addEventListener('click', function () {
var abrir = menu.dataset.aberto !== 'true';
definirMenu(abrir);
if (abrir) { var primeiro = menu.querySelector('a'); if (primeiro) primeiro.focus(); }
});
menu.addEventListener('click', function (e) { if (e.target.closest('a')) definirMenu(false); });
doc.addEventListener('keydown', function (e) {
if (e.key === 'Escape' && menu.dataset.aberto === 'true') { definirMenu(false); botaoMenu.focus(); }
if (e.key === 'Tab' && menu.dataset.aberto === 'true') {
var focaveis = [botaoMenu].concat(todos('a,button', menu));
var ultimo = focaveis[focaveis.length - 1];
if (e.shiftKey && doc.activeElement === botaoMenu) { e.preventDefault(); ultimo.focus(); }
else if (!e.shiftKey && doc.activeElement === ultimo) { e.preventDefault(); botaoMenu.focus(); }
}
});
consultaLarga.addEventListener('change', function () { definirMenu(false); });
}
var flutuante = doc.querySelector('.wa-flutuante');
var topo = doc.querySelector('.topo');
var ultimoY = window.scrollY;
var ajustarMoldura = function (y) {
if (flutuante) flutuante.dataset.oculto = y < 480 ? 'true' : 'false';
if (topo && !reduzir) {
if (doc.body.dataset.menu) topo.dataset.recolhido = 'false';
else if (y < 240 || y < ultimoY - 3) topo.dataset.recolhido = 'false';
else if (y > ultimoY + 3) topo.dataset.recolhido = 'true';
}
ultimoY = y;
};
ajustarMoldura(ultimoY);
todos('[data-cascata]').forEach(function (grupo) {
Array.prototype.forEach.call(grupo.children, function (filho, i) {
filho.classList.add('revela');
filho.dataset.atraso = String(Math.min(i, 5) * 80);
});
});
var alvos = todos('.revela');
if (alvos.length && !reduzir && 'IntersectionObserver' in window) {
var armados = [];
var revelar = function (el) {
if (el.dataset.atraso) el.style.transitionDelay = el.dataset.atraso + 'ms';
el.classList.add('is-visible');
el.classList.remove('is-armed');
};
var observador = new IntersectionObserver(function (entradas) {
entradas.forEach(function (entrada) {
if (!entrada.isIntersecting) return;
revelar(entrada.target);
observador.unobserve(entrada.target);
});
}, { rootMargin: '0px 0px -8% 0px', threshold: 0.04 });
var dobra = window.innerHeight;
armados = alvos.filter(function (el) { return el.getBoundingClientRect().top >= dobra * 0.95; });
armados.forEach(function (el) {
el.classList.add('is-armed');
observador.observe(el);
});
window.addEventListener('beforeprint', function () { armados.forEach(revelar); });
}
if (!reduzir) {
raiz.classList.add('imersivo');
var definirLargo = function () { raiz.classList.toggle('imersivo-largo', consultaLarga.matches); };
definirLargo();
var vh = window.innerHeight, largura = window.innerWidth, alturaDoc = 1;
var limitar = function (v, a, b) { return Math.min(b, Math.max(a, v)); };
var barra = doc.querySelector('.progresso span');
var derivas = todos('[data-deriva]');
var paralaxes = todos('.paralaxe img').map(function (img) { return { el: img, topo: 0, altura: 0 }; });
var flutuantes = todos('[data-flutua]').map(function (el) { return { el: el, topo: 0, altura: 0 }; });
var quadroHeroi = doc.querySelector('.heroi__foto');
var faixas = todos('[data-faixa]').map(function (el) { return { el: el, caixa: el.parentNode, topo: 0, altura: 0, excesso: 0 }; });
var palcos = todos('[data-palco]').map(function (el) { return { el: el, topo: 0, altura: 0, palavras: todos('.palavra', el), ultimo: -1 }; });
var pistas = todos('[data-pista]').map(function (el) { return { el: el, trilho: el.querySelector('.passos'), barra: el.querySelector('.pista__barra span'), topo: 0, distancia: 0 }; });
var cortinas = todos('[data-cortina]').map(function (el) { return { el: el, topo: 0, ultimo: -1 }; });
var topoDe = function (el) { return el.getBoundingClientRect().top + window.scrollY; };
var medir = function () {
vh = window.innerHeight;
largura = window.innerWidth;
definirLargo();
if (!consultaLarga.matches) {
cortinas.forEach(function (c) { c.el.style.clipPath = ''; c.ultimo = -1; });
}
pistas.forEach(function (p) {
if (!p.trilho) return;
if (consultaLarga.matches) {
p.distancia = Math.max(0, p.trilho.scrollWidth - largura);
p.el.style.height = (vh + p.distancia) + 'px';
} else {
p.distancia = 0;
p.el.style.height = '';
p.trilho.style.transform = '';
}
p.topo = topoDe(p.el);
});
paralaxes.concat(flutuantes).forEach(function (i) {
var caixa = i.el.parentNode.getBoundingClientRect();
i.topo = caixa.top + window.scrollY;
i.altura = caixa.height;
});
faixas.forEach(function (f) {
var r = f.caixa.getBoundingClientRect();
f.topo = r.top + window.scrollY;
f.altura = r.height;
f.excesso = Math.max(0, f.el.scrollWidth - largura);
});
palcos.forEach(function (p) { var r = p.el.getBoundingClientRect(); p.topo = r.top + window.scrollY; p.altura = r.height; });
cortinas.forEach(function (c) { c.topo = topoDe(c.el); });
alturaDoc = Math.max(1, doc.documentElement.scrollHeight - vh);
};
var desenhar = function () {
agendado = false;
var y = window.scrollY;
ajustarMoldura(y);
if (barra) barra.style.transform = 'scaleX(' + limitar(y / alturaDoc, 0, 1).toFixed(4) + ')';
if (y < vh * 1.3) {
var fator = consultaLarga.matches ? 0.2 : 0.09;
derivas.forEach(function (d) { d.style.transform = 'translate3d(' + (Number(d.dataset.deriva) * y * fator).toFixed(1) + 'px,0,0)'; });
if (quadroHeroi) quadroHeroi.style.setProperty('--quadro', (y * -0.05).toFixed(1) + 'px');
}
paralaxes.forEach(function (i) {
if (y + vh < i.topo - 40 || y > i.topo + i.altura + 40) return;
var pos = (i.topo + i.altura / 2 - (y + vh / 2)) / (vh + i.altura);
i.el.style.transform = 'translate3d(0,' + (pos * i.altura * 0.16).toFixed(1) + 'px,0) scale(1.12)';
});
flutuantes.forEach(function (i) {
if (y + vh < i.topo - 40 || y > i.topo + i.altura + 40) return;
i.el.style.transform = 'translate3d(0,' + (y * 0.07).toFixed(1) + 'px,0)';
});
faixas.forEach(function (f) {
if (y + vh < f.topo || y > f.topo + f.altura) return;
var pos = (y + vh - f.topo) / (vh + f.altura);
f.el.style.transform = 'translate3d(' + (-pos * f.excesso).toFixed(1) + 'px,0,0)';
});
palcos.forEach(function (p) {
if (y + vh * 1.5 < p.topo) return;
var total = p.altura - vh;
var pos = total > 0 ? limitar((y - p.topo + vh * 0.25) / total, 0, 1) : limitar((y + vh * 0.75 - p.topo) / vh, 0, 1);
if (Math.abs(pos - p.ultimo) < 0.004) return;
p.ultimo = pos;
var n = p.palavras.length;
p.palavras.forEach(function (w, i) {
w.style.opacity = (0.16 + 0.84 * limitar(pos * n * 1.2 - i, 0, 1)).toFixed(2);
});
});
pistas.forEach(function (p) {
if (!p.distancia || !p.trilho) return;
var pos = limitar((y - p.topo) / p.distancia, 0, 1);
p.trilho.style.transform = 'translate3d(' + (-pos * p.distancia).toFixed(1) + 'px,0,0)';
if (p.barra) p.barra.style.transform = 'scaleX(' + pos.toFixed(4) + ')';
});
if (consultaLarga.matches) {
cortinas.forEach(function (c) {
var pos = limitar((y + vh - c.topo) / (vh * 0.7), 0, 1);
if (pos === c.ultimo) return;
c.ultimo = pos;
c.el.style.clipPath = pos >= 1 ? '' : 'inset(0 ' + ((1 - pos) * 2.5).toFixed(2) + 'vw)';
});
}
};
var agendado = false;
var agendar = function () { if (!agendado) { agendado = true; window.requestAnimationFrame(desenhar); } };
window.addEventListener('scroll', agendar, { passive: true });
var remedir = function () { medir(); agendar(); };
consultaLarga.addEventListener('change', remedir);
var espera;
window.addEventListener('resize', function () { window.clearTimeout(espera); espera = window.setTimeout(remedir, 150); });
window.addEventListener('load', remedir);
window.requestAnimationFrame(remedir);
var fonteLenis = scriptAtual && scriptAtual.dataset.lenis;
if (fonteLenis && window.matchMedia('(pointer:fine)').matches) {
window.addEventListener('load', function () {
var s = doc.createElement('script');
s.src = fonteLenis;
s.onload = function () {
if (!window.Lenis) return;
var rolagem = new window.Lenis({ autoRaf: true, lerp: 0.09 });
doc.addEventListener('click', function (e) {
var link = e.target.closest('a[href^="#"]');
if (!link) return;
var id = link.getAttribute('href').slice(1);
var destino = id && doc.getElementById(id);
if (!destino) return;
e.preventDefault();
rolagem.scrollTo(window.scrollY + destino.getBoundingClientRect().top - 84);
window.history.pushState(null, '', '#' + id);
destino.setAttribute('tabindex', '-1');
destino.focus({ preventScroll: true });
});
};
doc.head.appendChild(s);
});
}
} else {
window.addEventListener('scroll', function () { ajustarMoldura(window.scrollY); }, { passive: true });
}
var mapa = doc.querySelector('[data-mapa-rosto]');
if (mapa) {
var linhas = todos('.linha[data-regiao]', mapa);
var grupos = todos('.r-grupo', mapa);
var legenda = mapa.querySelector('[data-mapa-legenda]');
var ativar = function (linha) {
if (linha.classList.contains('is-ativa')) return;
linhas.forEach(function (l) { l.classList.toggle('is-ativa', l === linha); });
grupos.forEach(function (g) { g.classList.toggle('is-ativo', g.dataset.regiao === linha.dataset.regiao); });
if (legenda) {
legenda.innerHTML = '';
var nome = doc.createElement('b');
nome.textContent = linha.dataset.nome;
var texto = doc.createElement('span');
texto.textContent = (linhas.indexOf(linha) + 1) + ' de ' + linhas.length + '. Referência: ' + linha.dataset.rotulo + '.';
legenda.appendChild(nome);
legenda.appendChild(texto);
}
};
linhas.forEach(function (linha) {
linha.addEventListener('pointerenter', function () { ativar(linha); });
linha.addEventListener('focusin', function () { ativar(linha); });
});
if ('IntersectionObserver' in window && window.matchMedia('(min-width:1000px)').matches) {
var porRolagem = new IntersectionObserver(function (entradas) {
entradas.forEach(function (entrada) { if (entrada.isIntersecting) ativar(entrada.target); });
}, { rootMargin: '-45% 0px -45% 0px' });
linhas.forEach(function (l) { porRolagem.observe(l); });
}
}
var indice = doc.querySelector('.indice');
if (indice) {
var largo = window.matchMedia('(min-width:1100px)');
var ajustarIndice = function () { indice.open = largo.matches; };
ajustarIndice();
largo.addEventListener('change', ajustarIndice);
var linksIndice = todos('a', indice);
indice.addEventListener('click', function (e) { if (e.target.closest('a') && !largo.matches) indice.open = false; });
if ('IntersectionObserver' in window) {
var atual = new IntersectionObserver(function (entradas) {
entradas.forEach(function (entrada) {
if (!entrada.isIntersecting) return;
linksIndice.forEach(function (a) {
var ligado = a.getAttribute('href') === '#' + entrada.target.id;
a.classList.toggle('is-atual', ligado);
if (ligado) a.setAttribute('aria-current', 'location'); else a.removeAttribute('aria-current');
});
});
}, { rootMargin: '-20% 0px -70% 0px' });
linksIndice.forEach(function (a) {
var alvo = doc.getElementById(a.getAttribute('href').slice(1));
if (alvo) atual.observe(alvo);
});
}
}
todos('[data-mapa-google]').forEach(function (caixa) {
var botao = caixa.querySelector('button');
if (!botao) return;
botao.addEventListener('click', function () {
var quadro = doc.createElement('iframe');
quadro.src = caixa.dataset.mapaGoogle;
quadro.title = 'Mapa com a localização da Mabelly Aesthetics, no Setor Coimbra, em Goiânia';
quadro.loading = 'lazy';
quadro.referrerPolicy = 'strict-origin-when-cross-origin';
caixa.textContent = '';
caixa.appendChild(quadro);
registrar('ver_mapa', {});
});
});
var metaAnalytics = doc.querySelector('meta[name="analytics-id"]');
var idAnalytics = metaAnalytics ? metaAnalytics.content : '';
var CHAVE = 'consentimento-cookies';
var lerEscolha = function () { try { return window.localStorage.getItem(CHAVE); } catch (e) { return null; } };
var gravarEscolha = function (v) { try { window.localStorage.setItem(CHAVE, v); } catch (e) {  } };
var analyticsLigado = false;
function ligarAnalytics() {
if (analyticsLigado || !idAnalytics) return;
analyticsLigado = true;
window.dataLayer = window.dataLayer || [];
window.gtag = function () { window.dataLayer.push(arguments); };
window.gtag('consent', 'default', { analytics_storage: 'granted', ad_storage: 'denied', ad_user_data: 'denied', ad_personalization: 'denied' });
window.gtag('js', new Date());
window.gtag('config', idAnalytics, { anonymize_ip: true });
var s = doc.createElement('script');
s.async = true;
s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(idAnalytics);
doc.head.appendChild(s);
if (doc.body.dataset.tratamento) registrar('ver_tratamento', { tratamento: doc.body.dataset.tratamento });
}
function registrar(nome, detalhe) {
if (analyticsLigado && window.gtag) window.gtag('event', nome, detalhe || {});
}
function mostrarAvisoCookies() {
if (doc.querySelector('.cookies')) return;
var aviso = doc.createElement('section');
aviso.className = 'cookies';
aviso.setAttribute('aria-label', 'Preferências de cookies');
var texto = doc.createElement('p');
texto.append('Usamos cookies de medição para entender como o site é usado, somente com a sua autorização. Saiba mais na ');
var link = doc.createElement('a');
link.href = '/politica-de-privacidade/';
link.textContent = 'Política de Privacidade';
texto.append(link, '.');
var acoes = doc.createElement('div');
acoes.className = 'acoes';
[['Recusar', 'recusado'], ['Aceitar', 'aceito']].forEach(function (par) {
var b = doc.createElement('button');
b.type = 'button';
b.className = 'btn';
b.textContent = par[0];
b.addEventListener('click', function () {
gravarEscolha(par[1]);
aviso.remove();
if (par[1] === 'aceito') ligarAnalytics();
});
acoes.appendChild(b);
});
aviso.append(texto, acoes);
doc.body.appendChild(aviso);
}
if (idAnalytics) {
var escolha = lerEscolha();
if (escolha === 'aceito') ligarAnalytics();
else if (escolha !== 'recusado') mostrarAvisoCookies();
todos('[data-preferencias-cookies]').forEach(function (b) { b.addEventListener('click', mostrarAvisoCookies); });
}
doc.addEventListener('click', function (e) {
var a = e.target.closest('a[href]');
if (!a) return;
var href = a.getAttribute('href') || '';
if (href.indexOf('wa.me') > -1 || href.indexOf('/whatsapp') === 0) registrar('contato_whatsapp', { origem: a.dataset.origem || doc.title });
else if (href.indexOf('tel:') === 0) registrar('contato_telefone', {});
else if (href.indexOf('instagram') > -1) registrar('contato_instagram', {});
else if (href.indexOf('maps.app') > -1) registrar('contato_mapa', {});
else if (href.indexOf('/agendamento') === 0) registrar('clique_agendamento', { origem: a.dataset.origem || doc.title });
});
var form = doc.querySelector('[data-form-avaliacao]');
if (form) {
var telefone = form.elements.telefone;
var mensagensErro = {
nome: 'Informe o seu nome.',
telefone: 'Informe um telefone com DDD, como (62) 90000-0000.',
interesse: 'Escolha uma opção.',
consentimento: 'Para continuar, é preciso concordar com o uso dos dados para este contato.'
};
var definirErro = function (campo, mensagem) {
var erro = doc.getElementById('erro-' + campo.name);
if (erro) erro.textContent = mensagem || '';
if (mensagem) campo.setAttribute('aria-invalid', 'true'); else campo.removeAttribute('aria-invalid');
};
var digitos = function (v) { return v.replace(/\D/g, ''); };
var telefoneOk = function (v) { var d = digitos(v); return d.length === 10 || d.length === 11; };
var validarCampo = function (campo) {
var ok = campo.type === 'checkbox' ? campo.checked : campo.value.trim() !== '';
if (ok && campo.name === 'telefone') ok = telefoneOk(campo.value);
definirErro(campo, ok ? '' : mensagensErro[campo.name]);
return ok;
};
if (telefone) {
telefone.addEventListener('input', function () {
var d = digitos(telefone.value).slice(0, 11);
var saida = d;
if (d.length > 2) saida = '(' + d.slice(0, 2) + ') ' + d.slice(2);
if (d.length > 6) {
var meio = d.length === 11 ? 7 : 6;
saida = '(' + d.slice(0, 2) + ') ' + d.slice(2, meio) + '-' + d.slice(meio);
}
telefone.value = saida;
});
}
var obrigatorios = ['nome', 'telefone', 'interesse', 'consentimento']
.map(function (n) { return form.elements[n]; })
.filter(Boolean);
obrigatorios.forEach(function (campo) {
campo.addEventListener('blur', function () { if (campo.getAttribute('aria-invalid') === 'true') validarCampo(campo); });
campo.addEventListener('change', function () { if (campo.getAttribute('aria-invalid') === 'true') validarCampo(campo); });
});
var dataCampo = form.elements.data;
if (dataCampo) {
var hoje = new Date();
hoje.setMinutes(hoje.getMinutes() - hoje.getTimezoneOffset());
dataCampo.min = hoje.toISOString().slice(0, 10);
}
var parametros = new URLSearchParams(window.location.search);
if (form.elements.interesse && parametros.get('interesse')) {
Array.prototype.forEach.call(form.elements.interesse.options, function (o) {
if (o.dataset.slug === parametros.get('interesse')) form.elements.interesse.value = o.value;
});
}
form.addEventListener('submit', function (e) {
e.preventDefault();
var invalidos = obrigatorios.filter(function (c) { return !validarCampo(c); });
if (invalidos.length) { invalidos[0].focus(); return; }
var valor = function (n) { var c = form.elements[n]; return c ? String(c.value || '').trim() : ''; };
var linhas = [
'Olá! Acessei o site da Elsângela Melo e gostaria de solicitar uma avaliação.',
'',
'Nome: ' + valor('nome'),
'Telefone: ' + valor('telefone'),
'Interesse: ' + valor('interesse')
];
if (valor('data')) linhas.push('Data de preferência: ' + valor('data').split('-').reverse().join('/'));
if (valor('periodo')) linhas.push('Período de preferência: ' + valor('periodo'));
if (valor('mensagem')) linhas.push('Mensagem: ' + valor('mensagem'));
registrar('envio_formulario', { interesse: valor('interesse') });
var url = 'https://wa.me/' + form.dataset.whatsapp + '?text=' + encodeURIComponent(linhas.join('\n'));
var status = form.querySelector('[data-form-status]');
if (status) {
status.hidden = false;
var alternativo = status.querySelector('a');
if (alternativo) alternativo.href = url;
status.focus();
}
window.open(url, '_blank', 'noopener');
});
}
todos('[data-copiar]').forEach(function (botao) {
var rotulo = botao.querySelector('b');
var original = rotulo ? rotulo.textContent : '';
botao.addEventListener('click', function () {
if (!navigator.clipboard) return;
navigator.clipboard.writeText(botao.dataset.copiar).then(function () {
if (rotulo) {
rotulo.textContent = 'Telefone copiado';
window.setTimeout(function () { rotulo.textContent = original; }, 2200);
}
});
});
});
})();