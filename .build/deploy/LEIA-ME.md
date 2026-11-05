# Como manter e publicar o site

Para quem é: quem mantém o site no servidor.

## Atenção: esta pasta é a produção

`/root/apexvilla/sites/elsangelamelo` é montada diretamente no container `elsangelamelo-web`. **Tudo que é salvo ou trocado de branch nessa pasta entra no ar na hora.** Trabalhe em um `git worktree` fora dela e publique com merge.

## Alterar conteúdo

1. Edite `.build/dados.py` (fatos), `.build/paginas/` (textos), `.build/build.py` (páginas), `.build/estilo.css` ou `.build/site.js`.
2. Gere e valide:
   ```bash
   python3 .build/build.py
   python3 .build/validar.py
   ```
3. Ícones e imagens sociais, só se a marca ou os títulos mudarem. Requer `playwright-core` e Google Chrome:
   ```bash
   python3 .build/gerar_marca.py
   PW_DIR=<pasta node_modules> TMP_OG=<pasta temporária> node .build/og.mjs
   ```
4. Testes em navegador, com uma prévia rodando. Requer `playwright-core` e `axe-core`:
   ```bash
   PW_DIR=<pasta node_modules> BASE=http://127.0.0.1:<porta> SAIDA=<pasta> node .build/testes/navegador.mjs
   ```

As pastas `.build` e `.docs` respondem 403 em produção, pela regra de arquivos ocultos do nginx.

## Publicar esta reestruturação

Faça nesta ordem. Os dois arquivos de configuração ficam fora deste repositório:

1. **Site:** `git -C /root/apexvilla/sites/elsangelamelo merge --ff-only origin/reestruturacao-premium`
2. **nginx:** faça backup e copie `.build/deploy/default.conf` para `/root/apexvilla/deploy/elsangelamelo/nginx/default.conf`. Depois: `docker exec elsangelamelo-web nginx -t && docker exec elsangelamelo-web nginx -s reload`
3. **Traefik:** faça backup e troque o `contentSecurityPolicy` de `/root/apex-erp/deploy/traefik/dynamic/elsangelamelo.yml` pelo conteúdo de `.build/deploy/traefik-csp.txt`. O Traefik recarrega sozinho. Atualize também o comentário do arquivo: os hashes de script inline deixaram de existir. Esse arquivo pertence ao repositório `apex-erp`.
4. **Conferência no ar:** home, um tratamento, `/tratamentos/peeling` (301), `/whatsapp` (302), `/.build/build.py` (403), o botão "Mostrar mapa" e o console do navegador.
5. **Search Console:** reenviar `sitemap.xml` e pedir indexação da home e de `/blog/cuidados-apos-preenchimento-labial/`.

**Reverter:** `git -C /root/apexvilla/sites/elsangelamelo reset --hard <commit anterior>` e restaurar os dois backups. O `reset` é destrutivo, então confirme o commit antes.

## Quando houver ID do Google Analytics 4

1. Preencha `GA4_ID` em `.build/dados.py` e gere o site. O aviso de cookies passa a aparecer, e o GA4 só carrega depois do aceite.
2. Atualize a política de privacidade (seção 6), como ela mesma promete, **antes** de publicar.
3. Amplie a CSP, ou o script será bloqueado:
   - `script-src 'self' https://www.googletagmanager.com`
   - `connect-src 'self' https://*.google-analytics.com https://*.analytics.google.com https://*.googletagmanager.com`
   - `img-src 'self' data: https://*.google-analytics.com https://*.googletagmanager.com`

Eventos preparados: `contato_whatsapp`, `contato_telefone`, `contato_instagram`, `contato_mapa`, `clique_agendamento`, `envio_formulario` (só com o tratamento de interesse), `ver_mapa` e `ver_tratamento`. Nome, telefone e mensagem nunca são enviados.

## Bibliotecas e fontes de terceiros

- Lenis 1.3.27 (MIT), em `.build/vendor/`: rolagem suave, carregada só com mouse e sem preferência por movimento reduzido.
- Bodoni Moda e Hanken Grotesk (SIL OFL), em `assets/fonts/`, recortadas para o alfabeto latino.
