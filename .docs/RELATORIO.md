# Relatório: reestruturação de elsangelamelo.com

Data: 5 de novembro de 2026. Estado: **publicado em 5 de novembro de 2026.**

> **Atualização de 5 de novembro de 2026, depois da publicação:** entraram os dados confirmados por Samir: CRBM da 3ª Região, formação, grafia MaBelly, avaliação gratuita, "+500 pacientes" e limpeza de pele como oitavo tratamento, com página própria. Os resultados agora direcionam ao Instagram, sem galeria no site. As seções abaixo descrevem a reestruturação inicial; as medições da seção G são anteriores a estes ajustes.

## A. Diagnóstico inicial

**Críticos, no ar antes desta reestruturação**
- Colchetes `[INSERIR ...]` públicos em quatro páginas: home, `/sobre/`, `/resultados/` (quatro blocos vazios) e `/politica-de-privacidade/` (razão social e CNPJ).
- Números sem comprovação: "+500 pacientes", "6 anos", "nota 5.0".
- "Revisado por Elsângela Melo" nos 5 artigos, sem registro dessa revisão.
- Título "Resultados reais" em uma página sem nenhum resultado.
- Orientação para sinais de alerta após o preenchimento sem alternativa se a profissional não respondesse.
- Promessas e termos inconsistentes: "resultados discretos, seguros", "viço radiante", "botox", "a equipe" e um oitavo serviço ("limpeza de pele") só em `/agendamento/`.
- Prováveis erros clínicos e afirmações regulatórias sem fonte (lista em `PENDENCIAS.md`).
- Política de privacidade incorreta: ignorava o formulário de `/agendamento/` e o Cloudflare.

**Técnicos**
- Coordenadas no schema a cerca de 1,4 km do local real.
- Canonical de `/agendamento` e `/links` apontando para URLs que redirecionam.
- `/links` e `/agendamento` indexáveis, competindo com `/contato/`.
- `MedicalBusiness` usado sem validação, e propriedades inválidas em `MedicalProcedure`.
- Google Fonts e 86 KB de CSS bloqueando a renderização (cerca de 1,1 s no celular).
- 495 KB de JavaScript antigo sem uso publicado; `favicon.png` que na verdade era um JPEG.
- Texto alternativo falso: "em atendimento na clínica" em um retrato de estúdio.
- H1 da home sem nome, profissão ou cidade. Cabeçalho e rodapé copiados em 20 páginas.

**Risco de operação:** a pasta do repositório é a própria raiz de produção. Qualquer arquivo salvo ou troca de branch nela entra no ar na hora.

**Search Console:** a indexação não é o problema (21 páginas indexadas). São 1 clique e 91 impressões em 28 dias, quase todas de marca. Falta visibilidade comercial.

## B. Melhorias implementadas

- **Identidade:** tipografia didona, da família visual do monograma, com a paleta original mantida. Fios no lugar de cartões, ícones e favicon refeitos, e imagem de compartilhamento por tratamento.
- **Mapa do rosto:** ilustração original em traço fino que destaca a região de cada tratamento, sem foto de banco.
- **Rolagem imersiva:** rolagem suave com o mouse; nome que se abre e fotos com profundidade; mapa que acompanha a descida; faixa de palavras; etapas da avaliação em trilho horizontal; frase que acende palavra por palavra; barra de progresso; cabeçalho que recolhe; transição entre páginas. Com movimento reduzido, tudo vira uma página comum.
- **Conteúdo:** nenhum colchete público. Dados não confirmados ficam em listas vazias e a seção não aparece. Foram aplicadas correções editoriais, de promessas e de contradições, e a orientação de urgência foi reforçada.
- **Conversão:** CTA no herói, no menu, no meio e no fim das páginas; WhatsApp com mensagem contextual por tratamento; formulário com validação, máscara de telefone, confirmação e link alternativo.
- **Privacidade:** fontes hospedadas no próprio site; mapa do Google só por clique; aviso de cookies e GA4 preparados, inativos até haver ID real. Política atualizada.
- **Manutenção:** gerador com fonte única (`.build/`), validador e testes automatizados.

## C. Páginas modificadas

- **Reescritas:** home, `/sobre/`, `/resultados/`, `/tratamentos/`, `/contato/`, `/blog/`, `/agendamento/`, `/links/`, `/politica-de-privacidade/`, 404.
- **Novo layout e textos corrigidos:** os 7 tratamentos e os 5 artigos. Cada tratamento ganhou figura, índice, bloco da profissional, tratamentos e artigos relacionados, e localização.
- **Removidas:** `/whatsapp/index.html` e `/instagram/index.html`, inalcançáveis porque o nginx já redireciona essas rotas.
- **URLs indexadas:** todas preservadas.

## D. SEO técnico

- Sitemap só com as 19 URLs canônicas e indexáveis, com `lastmod` real.
- `robots.txt` sem bloqueios desnecessários.
- Canonical corrigido em todas as páginas; `/agendamento/` e `/links/` em `noindex, follow`.
- Títulos e descrições únicos, um H1 por página e hierarquia de títulos corrigida.
- Redirecionamento 301 de `/tratamentos/<nome>/` para `/<nome>/`, e das imagens antigas para as novas (aplicado ao publicar).
- JSON-LD refeito (`Person`, `HealthAndBeautyBusiness`, `Service`, `BlogPosting`, `FAQPage`, `BreadcrumbList` e outros). Validador schema.org: **0 erros e 0 avisos em 10 páginas**.
- Segundo a imprensa especializada, o Google encerrou os rich results de FAQ em maio de 2026. A marcação foi mantida por corresponder ao conteúdo visível, mas não deve gerar destaque na busca.

## E. SEO local

- Coordenadas corrigidas conforme o perfil no Maps.
- Nome, endereço, telefone e horários a partir de uma fonte única, em todas as páginas.
- Variações de grafia reais vistas no Search Console e no Maps registradas nos dados estruturados: "Elisângela Melo", "MaBelly", "Ma Belly".
- Localização, mapa e botão "Como chegar", sem páginas artificiais por bairro.
- **Não feito:** o perfil no Google não foi alterado, por falta de acesso.

## F. SEO para mecanismos de IA

- Resposta direta no início de cada página.
- Autoria e registro identificados, entidades conectadas nos dados estruturados e HTML completo sem depender de JavaScript.
- `llms.txt` não foi criado, por não haver benefício comprovado.
- **Decisão pendente:** o robots gerenciado pelo Cloudflare bloqueia rastreadores como GPTBot, ClaudeBot e Google-Extended.
- Nenhuma promessa de recomendação por ChatGPT, Gemini ou Perplexity.

## G. Performance

Lighthouse no celular simulado, **medido em produção antes e depois**. Os números variam um pouco a cada execução.

| Métrica | Home antes | Home depois | Tratamento antes | Tratamento depois |
|---|---|---|---|---|
| Desempenho | 89 | 95 | 90 | 97 |
| Acessibilidade | 96 | 100 | 93 | 100 |
| Boas práticas | 100 | 100 | 100 | 100 |
| SEO | 92 | 92 | 92 | 92 |
| FCP | 2,8 s | 1,3 s | 2,8 s | 1,3 s |
| LCP | 3,0 s | 2,1 s | 2,8 s | 2,0 s |
| CLS | 0,029 | 0 | 0,067 | 0 |
| Peso | 202 KiB | 146 KiB | 123 KiB | 122 KiB |

No desktop, a home e o tratamento marcaram 100 em desempenho, acessibilidade e boas práticas, e 92 em SEO. **O SEO fica em 92 por causa da linha `Content-Signal` que o Cloudflare insere no `robots.txt`.** Sem essa linha, a prévia marcou 100. O Google ignora essa diretiva desconhecida, então a nota não indica problema de indexação. O INP não pode ser medido em laboratório: depende de dados reais de uso (o TBT da home ficou em 210 ms).

## H. Responsividade

- **Chrome:** 22 páginas em 9 larguras (320, 360, 390, 414, 768, 1024, 1280, 1440 e 1920 px), somando 198 combinações, sem rolagem lateral nem palavra partida em títulos, botões ou marca.
- **Firefox 157 e WebKit 27.2 (motor do Safari, com emulação de iPhone 14):** 9 páginas em desktop e celular, sem erros. O WebKit foi testado na prévia, em container descartável. O Firefox foi testado também em produção.
- **Dobra:** o botão de agendar fica visível em 320x568, 360x640, 390x664, 390x844 e 414x736.
- **Mudança de largura:** de larga para estreita e de volta (modo mobile do DevTools, tablet girado), sem recorte nem sobra de layout. Esse caso gerou um defeito real, relatado por Samir logo depois da publicação e corrigido.
- **Não testado:** aparelhos físicos.

## I. Acessibilidade

- axe-core (WCAG 2.0, 2.1 e 2.2, níveis A e AA, e boas práticas) em 22 páginas, em 390 e 1440 px, com movimento reduzido: **0 violações**. Com movimento ativo, os textos em transição de animação ficam temporariamente com menos contraste.
- Foco visível, link para pular conteúdo, menu com Esc e foco preso, erros de formulário ligados aos campos, `prefers-reduced-motion` e uso sem JavaScript testados.
- **Não testado:** leitor de tela real.

## J. Pendências

Lista completa em `.docs/PENDENCIAS.md`. Principais: formação e biografia, região do CRBM, comprovação dos números, revisão clínica dos textos, fotos em alta resolução, depoimentos e regra do conselho sobre antes e depois, CNPJ do controlador.

## K. Próximos passos

Em ordem de impacto provável para a visibilidade:

1. Reenviar o sitemap no Search Console e pedir indexação da home e de `/blog/cuidados-apos-preenchimento-labial/`.
2. Conferir o Perfil da Empresa no Google: nome, categoria, serviços, fotos e link para o site. Pedir avaliações a quem já foi atendido, sem incentivos.
3. Colocar o link do site na bio do Instagram e padronizar nome, endereço e telefone nos diretórios onde já existe cadastro.
4. Publicar formação e CRBM completo: é o maior ganho de confiança disponível.
5. Revisar e publicar os 5 artigos que faltam (`MAPA-PALAVRAS-CHAVE.md`).
6. Ativar o GA4 com o ID real e acompanhar cliques no WhatsApp por 90 dias.

O domínio aparece no Search Console há cerca de três meses e recebeu poucos cliques. Melhorias técnicas ajudam, mas não garantem posição: autoridade local tende a pesar tanto quanto elas.

## L. Problemas não resolvidos e limites

- **Traefik:** a CSP nova está ativa, mas `/root/apex-erp/deploy/traefik/dynamic/elsangelamelo.yml` ficou **modificado sem commit** no repositório `apex-erp`, que não faz parte desta tarefa. Um deploy a partir desse repositório pode voltar a CSP antiga e bloquear o mapa. Backups em `/root/apexvilla/deploy/elsangelamelo/backups-20261105/`.
- **Cache do Cloudflare:** ainda serve `favicon.png` e as imagens antigas de `/assets/` até o prazo expirar, sem efeito visível, pois as páginas usam os arquivos novos.
- **Conteúdo clínico:** continua sem revisão da profissional. As correções desta rodada são editoriais, sem consulta à literatura.
- **Fotos:** baixa resolução (682 a 959 px). Evitei foto em tela cheia por isso. Os tratamentos usam ilustração, não fotografia. AVIF não foi gerado por falta de codificador: as imagens estão em WebP.
- **Palavras-chave:** sem ferramenta de volume e sem análise confiável de concorrentes, porque a busca disponível não trouxe dados úteis de Goiânia.
- **Google Rich Results Test:** não foi executado. O validador usado foi o schema.org.
- **Harmonização de prazos:** onde as páginas se contradiziam, o texto passou a remeter à orientação recebida, sem número. A profissional ainda precisa definir os prazos que deseja publicar.
- **Registro profissional:** CRBM 17215 vem do próprio site e não foi confirmado em fonte externa.
- **Erros de console do PageSpeed:** não apareceram em Chrome, Firefox nem no Lighthouse em produção. Hipótese não confirmada: script injetado pelo Cloudflare só para os robôs do PageSpeed. Conferir no próprio PageSpeed.
- **Cloudflare e Perfil no Google:** alterações dependem de acesso.
- **Apex:** a tarefa não foi registrada, porque a ApexVilla não aparece entre as empresas autorizadas nesta conexão.
