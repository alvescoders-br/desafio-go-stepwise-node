# BRIEFING — Conduit Backend (Node / Express)

> **Documento-fonte de verdade deste repositório.** Toda etapa de planejamento e
> implementação **deve** seguir este guia. Ele traduz as diretrizes gerais do projeto
> (documento-fonte) para as particularidades **deste** código.
>
> **A pasta `documentacao/`, a pasta `harness/` e os arquivos `AGENTS.md` e
> `CLAUDE.md` NUNCA devem ser commitados.** Ver §13.

---

## 0. Como usar este documento (meta-instruções para o agente)

1. **Este guia tem precedência** sobre suposições e "boas práticas" genéricas. Em conflito,
   **vale este documento**.
2. **Imutabilidade de Arquitetura e Contrato.** O agente **não pode** alterar a arquitetura
   (estrutura de pastas por *feature*, camadas controller→service→Prisma, padrões de
   resposta) nem o **contrato da API RealWorld** por conta própria. As **únicas** mudanças
   permitidas são as de §4 e §5, exatamente no escopo descrito.
3. **Não previsto → PARE e peça permissão** (issue `needs-decision`). Ver §14.
4. **Issue antes de código.** Toda alteração referencia `#<id>`. Ver §6 e §7.
5. **Contrato externo imutável.** Os envelopes (`{ article }`, `{ articles, articlesCount }`,
   `{ user }`, `{ profile }`, `{ comment(s) }`, `{ tags }`) e o formato de erro
   `{ errors: { campo: ["msg"] } }` **não mudam**.

---

## 1. Identidade e baseline atual (estado a ser preservado)

| Item | Estado atual (exato) |
|---|---|
| Linguagem | **TypeScript 5.2.2** (alvo `es2015`, `strict` **desligado**) |
| Runtime/web | **Express 4.18.2** |
| ORM / Banco | **Prisma 4.16.2 + PostgreSQL** (singleton em `src/prisma/prisma-client.ts`) |
| Monorepo | **Nx 17.2.6** (projetos `api` e `e2e`; build `@nx/esbuild`, test `@nx/jest`) |
| Auth | **express-jwt 8.4.1** (HS256), header `Authorization: Token <jwt>` **ou** `Bearer` |
| Token | `jsonwebtoken 9.0.2`, payload `{ user: { id: number } }`, `expiresIn: '60d'` |
| Hash de senha | `bcryptjs 2.4.3` (custo 10) |
| Entry point | `src/main.ts` — cria `express()`, middlewares, **error handler global**, `app.listen` (⚠️ **não exporta `app`**) |
| Testes | Jest 29.7.0 + ts-jest; **unit** com Prisma mockado (`jest-mock-extended`); **e2e** Nx é boilerplate **stale** |
| Lint/format | ESLint 8.48 (Nx) + Prettier 2.6 (`{ singleQuote: true }`) |
| Docker | `Dockerfile` (single-stage, roda `dist/api` pré-buildado); **sem docker-compose** |
| CI | **Nenhum** |

**Variáveis de ambiente:** `DATABASE_URL` (sem fallback — obrigatória), `JWT_SECRET`
(fallback `'superSecret'`), `NODE_ENV`. Lidas inline, **sem módulo de config central**.

**Modelos Prisma (`src/prisma/schema.prisma`):** `User`, `Article`, `Comment`, `Tag`.
IDs são `Int autoincrement`. **Favorites** = relação implícita M:N
`User.favorites ↔ Article.favoritedBy` (join `_UserFavorites`) — **não há entidade
`Favorite`**.

---

## 2. Correções críticas ao documento-fonte (LEIA ANTES DE PLANEJAR)

O documento-fonte assume premissas que **não batem** com este repositório:

- **"Migrar para TypeScript" — JÁ ESTÁ EM TYPESCRIPT (100%).** Não há arquivos `.js` de
  código. **Não converta nada de JS para TS** e **não presuma Mongoose/MongoDB** — o banco
  é **PostgreSQL via Prisma**.
  - **Re-escopo autorizado desta tarefa:** "endurecer a tipagem" — habilitar `strict` no
    `tsconfig`, eliminar `any`/`@ts-ignore` (concentrados em `article.service.ts` e no error
    handler de `main.ts`). **Tratar a migração TS como melhoria de rigor de tipos**, não como
    conversão. (Confirmar escopo em issue antes — §14.)
- **"Dividir camadas monolíticas" — a arquitetura JÁ é dividida por feature e camada.** O
  **único monólito real** é `src/app/routes/article/article.service.ts` (**652 linhas**),
  que mistura artigo + **comentários** + **favoritos**; e o `article.controller.ts`
  (243 linhas) registra as rotas dos três juntos. **O alvo é extrair** `comment.*` e
  `favorite.*` (e o novo `bookmark.*`) para arquivos/pastas próprios — **não** "rebolar"
  pastas que já estão bem organizadas.
- **"Middleware centralizado de erros assíncronos" — já EXISTE um error handler global** no
  fim de `main.ts`. O trabalho real é **remover o `try/catch … next(error)` repetido em
  todos os controllers**, roteando erros assíncronos automaticamente (ex.: wrapper
  `asyncHandler` ou `express-async-errors`), **preservando** as 3 ramificações atuais do
  handler (express-jwt `UnauthorizedError` → 401; `HttpException.errorCode`; genérico 500).

> Estas correções **não autorizam** novas mudanças. Apenas alinham o plano à realidade.

---

## 3. Invariantes — o que PRESERVAR (proibido alterar sem permissão)

- **Estrutura por feature** (`article/`, `auth/`, `profile/`, `tag/`) e o padrão
  **controller → service → Prisma (+ mapper/util)**. Refatorações de §4 só **extraem**
  para novos arquivos; não inventam nova arquitetura (sem DI container, sem trocar Express
  por outro framework, etc., sem permissão).
- **Contrato da API RealWorld** (rotas, métodos, auth por rota, envelopes, formato de erro).
  Lista completa de endpoints no baseline; **todas** sob `/api` (via `routes.ts`).
- **Estratégia de auth** (express-jwt, esquema `Token`/`Bearer`, `req.auth.user.id: number`,
  payload `{ user: { id } }`) e o **fallback `JWT_SECRET='superSecret'`** (testes dependem
  dele — não remover sem atualizar testes).
- **Persistência Prisma + PostgreSQL** e o significado do flag `demo` nos filtros de
  consulta (`getArticles`, `getCommentsByArticle`, `getTags`, e `register` força
  `demo:false`).
- **IDs inteiros** e o formato de **slug** `${slugify(title)}-${id}`.
- **Singleton do PrismaClient** (`src/prisma/prisma-client.ts`), incluindo o cache em
  `global` quando `NODE_ENV==='development'`.

---

## 4. Mudanças AUTORIZADAS específicas deste projeto

### 4.1 "Migrar para TypeScript" → **Endurecer tipagem** *(re-escopo — ver §2)*
- Habilitar `strict` (ou progressivamente: `noImplicitAny`, `strictNullChecks`, …),
  remover `@ts-ignore`/`any` desnecessários, tipar o error handler de `main.ts`.
- **Sem** mudança de runtime, banco ou contrato.
- **Critério de aceite:** build/testes verdes com a tipagem mais estrita acordada; nenhuma
  mudança de comportamento.

### 4.2 Dividir o monólito `article.service.ts` em arquivos independentes
- **Extrair** de `article.service.ts` (652 linhas) e `article.controller.ts`:
  - `comment.service.ts` + `comment.controller.ts` (lógica de comentários);
  - `favorite.service.ts` + `favorite.controller.ts` (favoritar/desfavoritar).
- **Registrar** os novos controllers em `src/app/routes/routes.ts` (que monta os controllers
  por import — qualquer novo arquivo precisa ser registrado lá).
- **Preservar** assinaturas/efeitos observáveis (mesmas rotas, mesmos envelopes).
- **Critério de aceite:** comportamento idêntico; `article.service.ts` reduzido a artigos;
  testes verdes; nenhuma rota alterada.

### 4.3 Middleware centralizado de erros assíncronos
- **Remover** o `try/catch … next(error)` repetido em **todos** os handlers (article, auth,
  profile, tag), substituindo por um **wrapper `asyncHandler`** (ou `express-async-errors`).
- **Preservar** o error handler global de `main.ts` e suas 3 ramificações + o formato de erro
  do contrato. Não trocar o tipo `HttpException` (`errorCode` + `message`) sem permissão.
- **Critério de aceite:** nenhum `try/catch` boilerplate remanescente nos controllers; erros
  continuam produzindo os **mesmos** status/corpos de antes (verificado por testes de
  contrato/integração).

### 4.4 Rate limiting em `POST /api/users/login` + testes de integração
- **Net-new:** não há limiter hoje. Adicionar dependência (ex.: `express-rate-limit`) e
  aplicar o middleware **apenas** à rota de login em `src/app/routes/auth/auth.controller.ts`
  (`router.post('/users/login', …)`).
- **Testes de integração que acionam o limite:** disparar N requisições e verificar o
  bloqueio (HTTP 429) e os headers de rate limit.
- **Particularidade/lacuna:** **não há harness de integração** (sem `supertest`; `main.ts`
  **não exporta o `app`**; o e2e Nx não sobe servidor/banco e tem um teste *stale* afirmando
  `{ message: 'Hello API' }` enquanto o app responde `{ status: 'API is running on /api' }`).
  - **Decisão necessária (§14):** introduzir `supertest` + **refatorar `main.ts` em
    `app.ts` (export do `app`) e `server.ts` (`listen`)**, **ou** construir o bootstrap real
    no projeto `e2e`. A separação app/server é uma mudança estrutural mínima — **pedir
    permissão** antes, por afetar o entry point.
- **Critério de aceite:** limite configurável; teste de integração que comprova 429 ao
  exceder; rota de login intacta no caminho feliz.

### 4.5 Bookmarking — `POST /api/articles/:slug/bookmark` (autenticado)
- **Espelhar favoritos**, porém como marcação **pessoal** do usuário autenticado.
- **Referência a copiar:**
  - Rotas: `article.controller.ts` (`POST`/`DELETE /articles/:slug/favorite`,
    ambos `auth.required`, retornam `res.json({ article })`).
  - Service: `article.service.ts` linhas ~562–652 (`favoriteArticle`/`unfavoriteArticle`
    usando `connect`/`disconnect` na relação `favoritedBy`).
- **Banco (mudança autorizada de schema):** adicionar **nova relação implícita M:N**
  `User.bookmarks ↔ Article.bookmarkedBy` (relation `"UserBookmarks"`, join `_UserBookmarks`)
  → **requer nova migração Prisma** (`prisma migrate dev`). **Não** auto-sincronizar; gerar
  migração versionada.
- **Endpoints:** o documento-fonte cita **apenas POST**. **Ponto de permissão (§14):**
  decidir se haverá também `DELETE /api/articles/:slug/bookmark` por simetria com favoritos.
- **Organização:** implementar em `bookmark.service.ts` + `bookmark.controller.ts` (coerente
  com §4.2), registrados em `routes.ts`.
- **Critério de aceite:** usuário autenticado marca/desmarca; resposta segue o mesmo padrão
  de envelope; coberto por unit + integração; migração aplicável de forma limpa.

> **Ordem dependente:** 4.5 depende de 4.2 (estrutura) e se beneficia de 4.3 (sem try/catch).

---

## 5. Tarefas gerais (adaptadas a este repositório)

- **5.1 Issues + DoR/DoD + templates** — §6.
- **5.2 Conventional Commits + bleeding branch + GitAhead** — §7.
- **5.3 Containerização (Docker + Compose)** — §9 (compose com **PostgreSQL** + LGTM).
- **5.4 OpenAPI/Swagger do contrato atual** — §10.
- **5.5 Testes de contrato + integração** — §11.
- **5.6 E2E Playwright (API)** + **duas branches** (quebra/passa) — §11.
- **5.7 Teste de mutação (StrykerJS) — meta 95%** — §11.
- **5.8 Observabilidade LGTM** — §8.
- **5.9 Script Python** (Docker + logs start/stop) — §12.
- **5.10 Atualizar para versões mais recentes do framework** — **ponto de permissão**:
  Express 5, Prisma 5+, Nx atual e Node LTS são upgrades de impacto; planejar via issue e
  só executar com aprovação (não obrigatório para as tarefas 4.x).
- **5.11 Registro de prompts/skills** — §17.
- **5.12 Código e commits "com o Coda"** — convenção do time.

---

## 6. Disciplina de Issues (DoR / DoD)

- **Issue antes do trabalho**, via **templates do repositório**; todo commit referencia
  `#<id>`.
- **DoR:** escopo rastreável a §4/§5; critérios de aceite; invariantes (§3) a preservar
  listados; pontos de permissão (§14) resolvidos; plano de teste definido; **para mudanças
  de schema (4.5), a migração Prisma planejada**.
- **DoD:** critérios de aceite atendidos sem mudança não autorizada; **testes de contrato
  verdes** (sem regressão de API); integração + (quando aplicável) 429 do rate limit;
  cobertura de mutação na meta (§11); migração aplicável e reversível; Conventional Commits
  com `#<id>`; prompts/skills registrados (§17).

> DoR/DoD ajustáveis às preferências do time (via issue/permissão).

---

## 7. Commits, branches e GitAhead

- **Conventional Commits** com `#<id>`. Sugestão de escopos: `feat(bookmark):`,
  `refactor(article):`, `feat(ratelimit):`, `chore(errors):`.
- **Bleeding branch:** o harness comita progresso automaticamente (Conventional Commits).
- **GitAhead** para validar progresso/histórico.
- **Nunca** commitar os itens de §13.

---

## 8. Observabilidade (stack LGTM)

- **Loki/Grafana/Tempo/Mimir** no Compose.
- **Métrica de contador por endpoint** incrementando 1 a cada chamada — instrumentar com
  **OpenTelemetry/Prometheus** no Express (middleware contando por rota), exportando para
  **Mimir**.
- **Log na inicialização e no encerramento** da app — emitir no boot (`app.listen`) e no
  shutdown (sinais `SIGTERM`/`SIGINT`), enviados ao **Loki**.
- **Traces habilitados** (OpenTelemetry → **Tempo**), cobrindo handlers e chamadas ao Prisma.

> A separação app/server (§4.4) facilita a instrumentação. Manter o comportamento do
> contrato intacto.

---

## 9. Containerização (Docker + Compose)

- **Compose** orquestrando: serviço `api` (este backend), **PostgreSQL**, e a stack **LGTM**
  (§8). Variáveis: `DATABASE_URL`, `JWT_SECRET`, `NODE_ENV`.
- O `Dockerfile` atual roda o build pré-compilado (`dist/api`); ajustar o fluxo
  build→imagem no Compose (e migrações `prisma migrate deploy` na subida).
- Não commitar `dist/`, `coverage/`, `.env`.

---

## 10. Documentação da API (OpenAPI/Swagger)

- Documentar o **contrato atual** em **OpenAPI 3** (ex.: `swagger-jsdoc` +
  `swagger-ui-express`, ou geração a partir do código), cobrindo **todos** os endpoints sob
  `/api`, com os envelopes e o formato de erro.
- A spec OpenAPI é a **base dos testes de contrato** (§11) — divergência falha o teste.
- Incluir os **novos** endpoints de bookmark (§4.5) na spec quando implementados.

---

## 11. Estratégia de testes

1. **Testes de contrato (primeiro):** fixar o contrato atual (rotas, envelopes, erros) como
   rede de segurança **antes** das refatorações (4.2/4.3) e features (4.4/4.5).
2. **Testes de integração:** introduzir `supertest` (depende da decisão §4.4 sobre export do
   `app`) contra um Postgres de teste; cobrir auth, artigos, comentários, favoritos,
   **rate limit (429)** e **bookmark**.
3. **E2E Playwright (API):** fluxos ponta-a-ponta sobre a API; manter **uma branch com teste
   funcional quebrando** e **uma branch passando** (Playwright).
4. **Teste de mutação (StrykerJS):** meta **95%**. Atenção: hoje há lacunas (ex.:
   `tag.service.test.ts` é só `test.todo`; create/get/update/feed de artigos sem unit) — a
   meta exige ampliar os testes.

---

## 12. Script Python de validação (Docker + logs)

- Script Python que sobe via Compose, espera readiness, **valida logs de inicialização e
  de encerramento** (§8), e retorna sucesso/falha. Deve derrubar a stack ao final e ser
  utilizável em CI local.

---

## 13. Itens que NUNCA devem ser commitados

`documentacao/` · `harness/` · `AGENTS.md` · `CLAUDE.md`.

**Enforcement:** adicionados ao `.git/info/exclude` **local** (não versionado), para que
commits automáticos do harness não os capturem. **Não** colocá-los no `.gitignore`
versionado e **não** commitá-los manualmente.

---

## 14. Protocolo de permissão (quando PARAR e perguntar)

Abra issue `needs-decision` e aguarde aprovação antes de agir, quando:

- For necessária mudança de arquitetura/contrato **não listada** em §4/§5.
- For decidir **export do `app`/separação app-server** (§4.4) ou a estratégia de harness de
  integração.
- For decidir **`DELETE /bookmark`** (simetria com favoritos) — §4.5.
- For fazer **upgrades de framework** (Express 5, Prisma 5, Nx, Node) — §5.10.
- For mexer no **schema Prisma** de forma além da relação de bookmark prevista.
- O re-escopo da "migração TS" (§4.1) precisar ir além de `strict`/limpeza de tipos.

---

## 15. Roadmap sugerido (fases)

1. **Fundação:** issues/templates, DoR/DoD, bleeding branch, `.git/info/exclude` (§13).
2. **Rede de segurança:** OpenAPI + testes de contrato + harness de integração (decisão
   §4.4).
3. **Refino interno:** §4.1 (tipagem), §4.2 (split do monólito), §4.3 (erros assíncronos).
4. **Features:** §4.4 (rate limit + testes) e §4.5 (bookmark + migração).
5. **Qualidade:** mutação (Stryker) até 95%; E2E Playwright; branches passa/quebra.
6. **Operação:** Docker/Compose (+Postgres+LGTM), observabilidade, script Python.

> Ordem flexível ("não necessariamente nessa ordem"), **exceto** a rede de segurança
> (fase 2) antes das refatorações (fase 3).

---

## 16. Riscos e pontos de atenção (deste código)

- **`main.ts` não exporta `app`** → bloqueia integração com `supertest` sem refator (§4.4).
- **`DATABASE_URL` sem fallback** → nada roda (nem seed) sem Postgres + migrações aplicadas.
- **`JWT_SECRET` fallback `'superSecret'`** → testes dependem disso; não remover sem
  atualizar testes.
- **Bookmark = mudança de schema** (nova migração Prisma `_UserBookmarks`); não
  auto-sincronizar.
- **`demo` boolean** permeia filtros de consulta — atenção ao adicionar listagens.
- **`strict` desligado + `any`/`@ts-ignore`** concentrados em `article.service.ts` e no
  error handler.
- **e2e Nx atual é stale** (assert `Hello API`) — corrigir/realinhar ao real
  `API is running on /api`.

---
