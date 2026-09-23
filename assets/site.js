/* elsangelamelo.com — comportamento compartilhado das páginas estáticas.
   Regra: nada aqui pode ser pré-requisito para ler o conteúdo. O HTML já
   nasce completo e visível; este arquivo só acrescenta conforto. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── Menu mobile ─────────────────────────────────────────────────────── */
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    var setOpen = function (open) {
      nav.dataset.open = open ? 'true' : 'false';
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      toggle.setAttribute('aria-label', open ? 'Fechar menu' : 'Abrir menu');
    };
    setOpen(false);
    toggle.addEventListener('click', function () {
      setOpen(nav.dataset.open !== 'true');
    });
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) setOpen(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && nav.dataset.open === 'true') { setOpen(false); toggle.focus(); }
    });
  }

  /* ── Revelação em rolagem ────────────────────────────────────────────── */
  /* Três garantias para que conteúdo NUNCA fique preso invisível:
     1. só é escondido o que já nasce abaixo da dobra — o que está na tela
        inicial nunca é armado;
     2. um temporizador revela tudo o que sobrar, caso o observer não dispare
        (aba em segundo plano, captura de tela, navegador antigo);
     3. sem IntersectionObserver ou com movimento reduzido, nada é armado. */
  var targets = document.querySelectorAll('.js-reveal');
  if (targets.length && !reduceMotion && 'IntersectionObserver' in window) {
    var armados = [];
    var revelar = function (el) {
      el.classList.add('is-visible');
      el.classList.remove('is-armed');
    };

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        revelar(entry.target);
        io.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.05 });

    var alturaDobra = window.innerHeight;
    Array.prototype.forEach.call(targets, function (el, i) {
      if (el.getBoundingClientRect().top < alturaDobra * 0.95) return; // já visível
      el.classList.add('is-armed');
      el.style.transitionDelay = Math.min(i % 4, 3) * 70 + 'ms';
      armados.push(el);
      io.observe(el);
    });

    window.setTimeout(function () {
      armados.forEach(function (el) {
        if (!el.classList.contains('is-visible')) { revelar(el); io.unobserve(el); }
      });
    }, 2500);
  }

  /* ── Rastreamento de conversão ───────────────────────────────────────── */
  /* Empurra para o dataLayer se houver GTM; silencioso se não houver. Nada é
     enviado a terceiros por este arquivo — ele só emite o evento local. */
  var track = function (name, detail) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(Object.assign({ event: name }, detail || {}));
  };
  document.addEventListener('click', function (e) {
    var a = e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (href.indexOf('wa.me') > -1 || href.indexOf('/whatsapp') === 0) {
      track('contato_whatsapp', { origem: a.dataset.origem || document.title });
    } else if (href.indexOf('tel:') === 0) {
      track('contato_telefone', {});
    } else if (href.indexOf('instagram.com') > -1) {
      track('contato_instagram', {});
    } else if (href.indexOf('maps') > -1 || href.indexOf('/mapa') > -1) {
      track('contato_mapa', {});
    }
  });

  /* ── Formulário → WhatsApp ───────────────────────────────────────────── */
  /* Sem backend: monta a mensagem e entrega a conversa já escrita. Por isso
     nenhum dado pessoal trafega para servidor nosso — ver política de
     privacidade. */
  var form = document.getElementById('form-avaliacao');
  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var get = function (n) { var f = form.elements[n]; return f ? f.value.trim() : ''; };
      var linhas = [
        'Olá, Elsângela! Gostaria de agendar uma avaliação.',
        '',
        'Nome: ' + get('nome'),
        'Telefone: ' + get('telefone'),
        'Interesse: ' + get('interesse')
      ];
      if (get('mensagem')) linhas.push('Mensagem: ' + get('mensagem'));
      linhas.push('', '(enviado pelo site)');

      track('envio_formulario', { interesse: get('interesse') });

      var url = 'https://wa.me/5562982022330?text=' + encodeURIComponent(linhas.join('\n'));
      var aviso = document.getElementById('form-aviso');
      if (aviso) { aviso.hidden = false; aviso.focus(); }
      window.open(url, '_blank', 'noopener');
    });
  }

  /* ── Carrossel de depoimentos ────────────────────────────────────────── */
  var carrossel = document.querySelector('[data-carrossel]');
  if (carrossel) {
    var trilho = carrossel.querySelector('[data-carrossel-trilho]');
    var slides = trilho ? Array.prototype.slice.call(trilho.children) : [];
    var pontos = carrossel.querySelectorAll('[data-carrossel-ponto]');
    if (slides.length > 1) {
      var irPara = function (i) {
        slides[i].scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'nearest', inline: 'center' });
      };
      carrossel.querySelectorAll('[data-carrossel-nav]').forEach(function (btn) {
        btn.addEventListener('click', function () {
          var dir = btn.dataset.carrosselNav === 'prev' ? -1 : 1;
          var atual = slides.findIndex(function (s) {
            return Math.abs(s.getBoundingClientRect().left - trilho.getBoundingClientRect().left) < 40;
          });
          if (atual < 0) atual = 0;
          irPara(Math.max(0, Math.min(slides.length - 1, atual + dir)));
        });
      });
      pontos.forEach(function (p, i) { p.addEventListener('click', function () { irPara(i); }); });
    }
  }

  /* ── Ano do rodapé ───────────────────────────────────────────────────── */
  document.querySelectorAll('[data-ano]').forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });
})();
