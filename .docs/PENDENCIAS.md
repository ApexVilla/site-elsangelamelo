# Pendências que dependem de Elsângela Melo

Para quem é: Elsângela Melo e quem cuida do site. Nada desta lista está publicado como fato. Onde o site precisava do dado, a seção simplesmente não aparece até ele ser confirmado.

Como publicar um dado confirmado: preencher `.build/dados.py`, rodar `python3 .build/build.py` e `python3 .build/validar.py`.

## 1. Dados para confirmar ou enviar

| # | O que preciso | Situação no site |
|---|---|---|
| 1 | Graduação, pós-graduação, especializações, cursos e certificações, com curso, instituição e ano | Seção oculta |
| 2 | Biografia real: início na estética, motivação, trajetória e locais de atuação | Seção oculta |
| 3 | Confirmar o registro CRBM 17215 e a região do conselho | Publicado como já estava, sem a região |
| 4 | Comprovar "+500 pacientes", "6 anos de experiência" e "nota 5.0" | Removidos até haver confirmação |
| 5 | Fotos profissionais originais, em alta resolução, e fotos da clínica | Usando as fotos atuais, de baixa resolução (682 a 959 px de largura) |
| 6 | Depoimentos reais com autorização: texto, primeiro nome e procedimento | Seção oculta |
| 7 | Fotos de antes e depois com autorização por escrito | Galeria oculta. Ver item 9 |
| 8 | Grafia oficial da clínica: "Mabelly" (site) ou "MaBelly" (Google Maps) | Site usa "Mabelly"; a outra grafia está só nos dados estruturados |
| 9 | Regra do Conselho de Biomedicina sobre antes e depois | Não encontrei a regra em fonte confiável. Confirmar antes de publicar qualquer imagem |
| 10 | Razão social e CNPJ do controlador dos dados, para a política de privacidade | Linha oculta até ser informada |
| 11 | "Limpeza de pele" é um serviço oferecido? | Removido de `/agendamento/`, pois não está entre os 7 tratamentos |
| 12 | A avaliação é paga ou gratuita? | O site não diz |
| 13 | O telefone do perfil no Google é o mesmo (62) 98202-2330? | A conferir no perfil |

## 2. Revisão clínica obrigatória

Os 7 textos de tratamento e os 5 artigos não têm registro de revisão da profissional. A frase "Revisado por Elsângela Melo" foi retirada. Depois da leitura e da aprovação, basta marcar `CONTEUDO_REVISADO = True` em `.build/dados.py`, e a menção volta nas páginas e nos dados estruturados.

### Mudanças feitas nesta revisão que precisam do seu aval

- **Sinais de alerta:** o artigo de cuidados e a página de contato agora dizem para procurar um serviço de urgência se não for possível falar de imediato com a profissional. Antes, a orientação não tinha saída fora do horário de atendimento.
- **Bioestimuladores:** o texto dizia que o produto "não ocupa espaço no tecido" e que não há volume imediato. Agora diz que, em geral, esse não é o objetivo, embora alguns ativos tenham efeito inicial pelo gel.
- **Skinbooster:** "apoio à barreira cutânea" virou "melhorar a hidratação da pele".
- **Preenchimento labial:** edema "mais evidente nas primeiras 48 horas" virou "nos primeiros dias", para não contradizer o artigo de cuidados. Também entrou uma pergunta sobre o que significa 0,5 ml ou 1 ml, sem indicar quantidade.
- **Afirmações regulatórias sem fonte:** "privativos de profissionais de saúde" foi trocado por "devem ser realizados por profissional habilitado", e "restritos a maiores de 18 anos" foi retirado.

### Prazos que precisam da sua definição

As contradições abaixo foram retiradas do site com um texto neutro, sem inventar número. Se preferir publicar prazos, informe quais valem.

- **Álcool antes do procedimento:** as páginas diziam "24 horas", "horas anteriores" ou "véspera". Agora dizem "antes da sessão, conforme a orientação recebida".
- **Álcool depois do preenchimento:** a página do tratamento diz "primeiras 24 horas", e o artigo diz "24 a 48 horas". Qual vale?
- **Maquiagem labial:** a página dizia "primeiras horas", e o artigo, "primeiros dias". Agora a página diz "até a liberação da profissional".
- **Peeling:** o prazo de "poucos dias a cerca de uma semana" foi trocado por "varia conforme o tipo e a intensidade", porque não cobria todos os tipos citados.
- **Linhas em repouso:** o artigo sobre botox dizia que "o componente é estrutural". Agora diz que "pode haver também um componente estrutural".
- **Coagulação:** entrou em "Quando pode não ser indicado" em toxina botulínica e microagulhamento, como nas outras páginas. Confirme se está de acordo.
- **Durações e intervalos:** nenhuma página de tratamento informa números. Deseja publicar faixas?

### Práticas descritas que precisam ser verdadeiras

| Página | Afirmação |
|---|---|
| Todas | Avaliação presencial antes de qualquer procedimento; retorno de acompanhamento; produtos regularizados na ANVISA |
| Tratamentos (lista) | Avaliação reservada como consulta própria; valores apresentados junto do plano, sem obrigação de decidir na hora |
| Preenchimento labial | Agulha fina ou microcânula; rastreabilidade de lote; hialuronidase; canal aberto para dúvidas |
| Toxina botulínica | Retorno agendado; aplicação em raiz do nariz, cauda da sobrancelha, mento e bandas do pescoço |
| Bioestimuladores | Quais dos três ativos citados são usados; retornos programados; fotos usadas só para comparação clínica |
| Skinbooster | Aplicação em colo, dorso das mãos e região periorbital |
| Peeling | Oferta de peeling superficial, médio e profundo |
| Harmonização facial | Atuação em lábios e nariz; encaminhamento a outros profissionais quando necessário |
| Artigo "Como escolher" | Embalagem lacrada e lote registrado no prontuário; orientações por escrito; contato fora do horário |
| Política de privacidade | Acesso ao WhatsApp restrito a quem cuida do agendamento |
| Resultados | Nenhuma imagem de paciente sem autorização escrita, específica e revogável |

## 3. Decisões e acessos

| Tema | O que decidir ou fornecer |
|---|---|
| Google Analytics 4 | ID real da propriedade. Sem ele, não há analytics nem aviso de cookies |
| Search Console | Quais são as 3 páginas "não indexadas" do relatório |
| Perfil no Google | Acesso para conferir nome, categoria, telefone, horários, site, serviços e fotos. Nada foi alterado lá |
| Cloudflare: robots gerenciado | Hoje bloqueia GPTBot, ClaudeBot, Google-Extended e outros rastreadores de IA, e a linha `Content-Signal` derruba o SEO do Lighthouse para 92. O bloqueio pode ser desejado. Decidir conscientemente |
| Cloudflare: ocultação de e-mail | Troca o e-mail do HTML por `[email protected]` e injeta um script. Recomendo desligar |
| LGPD | Revisão jurídica da política, em especial transferência internacional (Meta, Google, Cloudflare) e encarregado de dados |
