# Guia didático do Playlist Editor — Loop Quick Small Feature

**Projeto:** <code>dojo-stepwise-5</code>  
**Playlist analisada:** <code>Loop Quick Small Feature</code> (<code>loop-quick-small-feature</code>)  
**Fonte principal:** [loop-quick-small-feature-agent-guide.json](../artifacts/outputs/playlist/loop-quick-small-feature-agent-guide.json)  
**Data da análise:** 2026-07-31

## 1. Objetivo

Este guia explica as 13 capabilities colocadas no canvas como referência: o que
cada uma faz, com quais capabilities combina melhor, quais artefatos devem ser
transferidos entre elas e que configurações usar quando forem escolhidas para
uma playlist real.

O canvas deve ser lido como uma biblioteca de lanes. Não é necessário — e
normalmente não é desejável — executar os 13 nós juntos. As composições viáveis
estão na seção 7.

## 2. Como ler o editor

Adicionar um nó não cria uma dependência. Uma playlist só fica executável quando:

1. os parâmetros de entrada estão preenchidos;
2. uma saída de uma capability é ligada à entrada compatível da próxima;
3. a continuação usa uma condição quando depende de veredicto;
4. todos os nós que serão executados são alcançáveis no DAG;
5. a capability e suas skills existem no registry do perfil Stepwise.

Os quatro campos mais importantes são:

| Campo | Significado | Exemplos |
|---|---|---|
| <code>init_params</code> | Configuração da execução. | <code>source_path</code>, <code>project_name</code>, <code>output_folder</code>. |
| <code>produces</code> | Estados/artefatos publicados. | <code>quick_story_output_path</code>, <code>runtime_status</code>. |
| <code>consumes</code> | Estados/artefatos necessários. | <code>quick_story_output_path</code>, <code>source_path</code>. |
| <code>condition</code> | Regra da transição. | <code>story_readiness == "READY_FOR_QUICK_CHANGE"</code>. |

A regra prática é:

~~~text
produtor.produces  ->  consumidor.consumes
~~~

O JSON atual tem 13 capabilities, 4 fases, 5 registros no DAG, 2 sinais e um
grupo iterativo. As três ligações de negócio que aparecem no centro da tela são
o núcleo abaixo:

~~~mermaid
flowchart LR
    A[Solicitação pequena] --> B[quick-story-definition]
    B -->|READY_FOR_QUICK_CHANGE| C[quick-change-implementation]
    C -->|APPLIED_VERIFIED ou APPLIED_UNVERIFIED| D[local-runtime-validation]
    B -->|não pronta| E[triagem / full lane]
    C -->|fora do envelope| F[code-development-autoloop]
~~~

## 3. Diagnóstico da composição atual

A composição atual é válida como painel de referência. Os pontos abaixo são
alertas apenas para o caso de alguém tentar executar todos os nós como um único
fluxo:

- Os nós de produto, arquitetura, QE, segurança, MCP e desenvolvimento
  completo aparecem na fase 1, mas não têm uma cadeia de artefatos que os torne
  alcançáveis a partir do início. Estar na mesma fase permite paralelismo, mas
  não cria dependência.
- <code>quick-story-definition.request_path</code> está vazio. Para uma
  execução reproduzível, informe um arquivo de solicitação ou garanta que
  <code>$.title</code>, <code>$.description</code> e <code>$.requirements</code>
  existam no payload da iteração.
- <code>sprint-planning</code> aponta para <code>artifacts/inputs/PRD.md</code> e
  <code>artifacts/inputs/epics</code>, enquanto <code>product-definition</code>
  grava em <code>artifacts/outputs/product-definition</code>. Em um fluxo
  integrado, escolha os outputs do <code>product-definition</code> como fonte.
- QE e desenvolvimento também apontam para PRD/épicos em
  <code>artifacts/inputs</code>. Isso só é correto se esses arquivos forem a
  fonte oficial; caso contrário, alinhe os paths.
- <code>software-architecture</code> e
  <code>software-architecture-autoloop</code> podem gravar a mesma arquitetura.
  Escolha uma como produtora oficial ou isole completamente os outputs.
- <code>local-runtime-validation.validated_test_cases_path</code> referencia
  <code>quality-engineering-web-automation</code>, que não está no canvas.
  Deixe vazio para smoke local ou adicione essa capability à playlist.
- O perfil local contém YAMLs para apenas parte dos 13 nós. As capabilities
  rápidas, <code>sprint-planning</code>, <code>static-security-analysis</code>,
  <code>mcp-tools-development</code> e
  <code>software-architecture-autoloop</code> aparecem no catálogo/playlist,
  mas não aparecem como YAML no diretório local de capabilities instalado.
  Antes de executar, valide o registry da versão efetivamente usada.

## 4. Mapa das 13 capabilities

| Capability | Fase | Propósito | Combina melhor com |
|---|---|---|---|
| <code>quick-story-definition</code> | Discovery | Transformar pedido pequeno em história pronta ou decisão de escalação. | Quick change, produto ou triagem. |
| <code>quick-change-implementation</code> | Development | Planejar e aplicar mudança localizada em modo rápido. | Quick story e runtime. |
| <code>sprint-planning</code> | Discovery | Dividir backlog em sub-objetivos iteráveis. | Grupo de implementação. |
| <code>local-runtime-validation</code> | Development | Bootstrap, launch, smoke API/browser, gate e teardown. | Qualquer lane de código. |
| <code>static-security-analysis</code> | Testing/Security | SAST, segredos, SCA, contêiner, IaC opcional e grafo de serviços. | Triagem de findings e reparo. |
| <code>code-development-autoloop</code> | Development | Pesquisa, plano, verificação, implementação e review com loop. | Arquitetura, QE e runtime. |
| <code>mcp-tools-development</code> | Development | Construir ferramentas MCP e integrações mock-first. | Design agentic, contratos e runtime. |
| <code>quality-engineering-planning</code> | Testing | Estratégia, master test plan e E2E. | Produto, arquitetura e QE design. |
| <code>quality-engineering-design</code> | Testing | Casos funcionais Gherkin por história. | QE planning e desenvolvimento. |
| <code>product-definition</code> | Discovery | PRD e épicos validados. | Arquitetura e product delivery. |
| <code>product-delivery</code> | Delivery | Histórias detalhadas, critérios e export de plataforma. | QE, sprint planning e desenvolvimento. |
| <code>software-architecture</code> | Discovery | Bounded contexts, ADRs, arquitetura-alvo e DTR. | Produto, delivery, QE, código e runtime. |
| <code>software-architecture-autoloop</code> | Discovery | Arquitetura com verificações automáticas de conformidade. | Produto, MCP e código. |

## 5. Fichas das capabilities

### 5.1 quick-story-definition

**Propósito.** Criar uma <code>QUICK-STORY-SPEC</code> compacta a partir de uma
solicitação de feature ou bug pequeno. A saída informa se o item está pronto
para o quick lane, se precisa do fluxo completo, se deve ser triado ou se deve
ser pulado.

**Melhores ligações.**

- Antes: <code>sprint-planning</code>, se houver fila.
- Depois: <code>quick-change-implementation</code> quando estiver pronto.
- Alternativa: <code>product-definition</code>/<code>product-delivery</code> ou
  gate humano.

**Configuração recomendada:**

~~~json
{
  "project_name": "project",
  "request_path": "$PROJECT_DIR/artifacts/inputs/small-feature-request.json",
  "story_type": "feature",
  "source_path": "$PROJECT_DIR/source",
  "context_pack_path": "$PROJECT_DIR/context-pack",
  "feature_id": "$.title",
  "output_folder": "$PROJECT_DIR/artifacts/outputs/quick-story-definition",
  "quick_story_output_folder": "quick-story-spec",
  "quick_story_output_path": "$PROJECT_DIR/artifacts/outputs/quick-story-definition/quick-story-spec",
  "custom_message": "Usar somente a solicitação delimitada; não ampliar o escopo."
}
~~~

**Produz:** <code>quick_story_output_path</code>,
<code>story_readiness</code> e <code>story_type_resolved</code>.

**Gate:** ligar ao quick change somente com
<code>story_readiness == "READY_FOR_QUICK_CHANGE"</code>. Os demais veredictos
devem escalar, ir para triagem ou acionar <code>signal-skip</code>.

### 5.2 quick-change-implementation

**Propósito.** Implementar uma mudança localizada sem o peso do RPI completo.
Trabalha em modo PLAN, que cria uma especificação, e APPLY, que aplica a
especificação aprovada, atualiza testes focados quando possível e valida a
alteração. Se a mudança ultrapassar o envelope rápido, deve escalar.

**Melhores ligações.**

- Entrada: <code>quick_story_output_path</code> e <code>source_path</code>.
- Depois: <code>local-runtime-validation</code>.
- Falha/escalação: <code>code-development-autoloop</code> em
  <code>bug-fixing</code> ou <code>feature-impl</code>.

~~~json
{
  "project_name": "project",
  "quick_story_path": "$PROJECT_DIR/artifacts/outputs/quick-story-definition/quick-story-spec",
  "source_path": "$PROJECT_DIR/source",
  "context_pack_path": "$PROJECT_DIR/context-pack",
  "feature_id": "$.title",
  "output_folder": "$PROJECT_DIR/artifacts/outputs/quick-change-implementation",
  "quick_change_output_folder": "quick-change-spec",
  "quick_change_output_path": "$PROJECT_DIR/artifacts/outputs/quick-change-implementation/quick-change-spec",
  "skip_runtime_validation": false,
  "custom_message": "Alterar somente a história aprovada."
}
~~~

**Produz:** <code>apply_verdict</code>, <code>change_verdict</code>,
<code>quick_change_output_path</code> e <code>source_path</code>.

**Gate:** a rota de runtime recomendada aceita
<code>APPLIED_VERIFIED</code> ou <code>APPLIED_UNVERIFIED</code>. Qualquer outro
resultado deve ir para reparo ou escalação. No JSON atual, a ligação para runtime
está incondicional; torne-a condicional se quiser fail-closed.

### 5.3 sprint-planning

**Propósito.** Transformar PRD/épicos ou documentos equivalentes em
<code>SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json</code>, a fila que alimenta
iterações.

**Quando usar.** Em backlog de várias pequenas mudanças. Para uma única feature
já bem definida, é opcional.

~~~json
{
  "project_name": "project",
  "prd_path": "$PROJECT_DIR/artifacts/outputs/product-definition/prd",
  "epics_path": "$PROJECT_DIR/artifacts/outputs/product-definition/epics",
  "output_folder": "$PROJECT_DIR/artifacts/outputs/sprint-planning",
  "chunking_criteria": "quickchange-scope-tripwire",
  "max_acceptance_checks_per_chunk": "7",
  "max_sub_goals": "20",
  "sub_goal_decomposition_path": "SUB-GOAL-DECOMPOSITION-{SESSION_ID}.json",
  "failure_feedback": ""
}
~~~

**Melhores ligações.** O output decomposto deve iniciar um grupo com
<code>loop_source_artifact: "sub_goal_decomposition_path"</code>. O tripwire
evita chamar de “pequena” uma mudança que já ultrapassa o quick lane.

### 5.4 local-runtime-validation

**Propósito.** Bootstrapar banco/serviços e <code>.env</code>, iniciar a
aplicação, fazer smoke de API/browser, passar por gate manual e desmontar os
serviços criados.

~~~json
{
  "input_folder": "$PROJECT_DIR/artifacts/inputs",
  "output_folder": "$PROJECT_DIR/artifacts/outputs/local-runtime-validation",
  "project_name": "project",
  "source_path": "$PROJECT_DIR/source",
  "dtr_path": "$PROJECT_DIR/artifacts/outputs/software-architecture/dtr*.md",
  "discovery_package_path": "",
  "validated_test_cases_path": "",
  "launch_targets": "auto",
  "application_urls": "",
  "monorepo_strategy": "auto",
  "smoke_mode": "auto",
  "db_strategy": "auto",
  "max_routes": 15,
  "max_probe_seconds": 120,
  "viewports": "desktop:1440x900,mobile:375x667",
  "max_fix_retries": 2,
  "cleanup_services": true,
  "teardown_grace_seconds": 5,
  "auth_headers_path": "",
  "bootstrap_output_folder": "bootstrap",
  "launch_output_folder": "launch",
  "smoke_output_folder": "smoke",
  "teardown_output_folder": "teardown",
  "consolidated_errors_filename": "consolidated-errors.json",
  "quality_criteria_path": "criteria/local-runtime-validation-criteria.md"
}
~~~

**Melhores ligações.** Entrada: <code>source_path</code> da implementação;
opcionais: <code>dtr_path</code>, casos de teste validados e headers. Saídas
principais: <code>runtime_status</code>, <code>runtime_info_path</code>,
<code>runtime_validation_feedback</code>, <code>consolidated_errors_path</code>,
<code>env_status</code>, <code>launch_status</code> e
<code>teardown_status</code>.

Mantenha <code>cleanup_services: true</code>. Se houver
<code>env_blockers</code>, não invente segredos. Um runtime falho deve alimentar
um reparo, não abrir automaticamente a próxima história.

### 5.5 static-security-analysis

**Propósito.** Validar autorização e escopo, registrar repositórios, executar
SAST, análise de segredos, SCA, contêiner e IaC opcional, produzindo findings
rotulados por evidência e grafo de dependências.

~~~json
{
  "project_name": "project",
  "intake_contract_path": "$PROJECT_DIR/artifacts/inputs/security-intake.json",
  "output_folder": "$PROJECT_DIR/artifacts/outputs/static-security-analysis",
  "repos_path": "$PROJECT_DIR/artifacts/work/repos",
  "staticanalyzer_api_base": "https://<ambiente-autorizado>/api",
  "model_policy_defaults_path": "$PROJECT_DIR/artifacts/inputs/security-model-policy.json",
  "enabled_tools": "sast,secrets,sca,container",
  "enable_deep_secrets": false,
  "enable_iac": false,
  "diagram_path": "$PROJECT_DIR/artifacts/outputs/software-architecture/target-architecture",
  "validated_intake_package_path": "intake-package",
  "consolidated_raw_findings_path": "findings",
  "service_dependency_graph_path": "service-graph",
  "custom_message": "Executar somente no escopo autorizado; não acessar produção."
}
~~~

**Melhores ligações.** Pode receber contexto da arquitetura. Depois dela devem vir
triagem/gate de segurança e, se necessário,
<code>code-development-autoloop</code> em <code>bug-fixing</code>. Não ligue
findings brutos diretamente ao quick change. Os estados relevantes são
<code>intake_status</code>, <code>scope_authorization_decision</code>,
<code>scan_status</code>, <code>graph_status</code> e
<code>analysis_review_decision</code>. Não use endpoints ou credenciais
fictícios.

### 5.6 code-development-autoloop

**Propósito.** Lane para alterações maiores ou de maior risco. Faz pesquisa,
planejamento, revisão de conformidade de plataforma, verificação do plano,
implementação, code review e gates. Pode reparar plano/implementação dentro de
limites controlados.

~~~json
{
  "input_folder": "$PROJECT_DIR/artifacts/inputs",
  "output_folder": "$PROJECT_DIR/artifacts/outputs/code-development-autoloop",
  "source_path": "$PROJECT_DIR/source",
  "project_name": "project",
  "feature_id": "$.title",
  "scope_type": "feature-impl",
  "task_description_path": "$.requirements",
  "prd_path": "$PROJECT_DIR/artifacts/outputs/product-definition/prd",
  "epics_path": "$PROJECT_DIR/artifacts/outputs/product-definition/epics",
  "user_stories_path": "$PROJECT_DIR/artifacts/outputs/product-delivery/user-stories",
  "test_cases_path": "$PROJECT_DIR/artifacts/outputs/quality-engineering-design/test-cases",
  "target_architecture": "$PROJECT_DIR/artifacts/outputs/software-architecture/target-architecture",
  "adr_path": "$PROJECT_DIR/artifacts/outputs/software-architecture/adrs",
  "domain_boundaries_path": "$PROJECT_DIR/artifacts/outputs/software-architecture/domain-boundaries",
  "quality_criteria_path": "criteria/code-development-criteria.md",
  "research_depth": "targeted",
  "review_scope": "targeted",
  "review_context_limit": "changed_and_deps",
  "skip_runtime_validation": false,
  "custom_message": "Executar somente a fatia descrita em $.requirements."
}
~~~

**Melhores ligações.** Recebe produto, arquitetura, QE e, para reparo, findings
triados ou feedback de runtime. Só deve liberar runtime quando
<code>review_status == "PASSED"</code>. Saídas principais: plano,
implementação, review, <code>review_feedback</code>, veredictos de conformidade e
<code>source_path</code>.

### 5.7 mcp-tools-development

**Propósito.** Construir ferramentas compatíveis com MCP para APIs e sistemas de
registro, usando mocks antes da integração real, validação de contrato e gate de
publicação.

~~~json
{
  "detailed_agent_design_path": "$PROJECT_DIR/artifacts/outputs/agentic/detailed-agent-design",
  "platform_blueprint_path": "$PROJECT_DIR/artifacts/outputs/agentic/platform-blueprint",
  "api_contracts_path": "$PROJECT_DIR/artifacts/outputs/agentic/api-contracts",
  "output_path": "$PROJECT_DIR/artifacts/outputs/mcp-tools-development",
  "source_path": "$PROJECT_DIR/source",
  "failure_feedback": ""
}
~~~

No canvas atual os quatro primeiros caminhos estão vazios. Preencha-os ou
remova este nó da playlist executável.

**Melhores ligações.** Antes: blueprint de plataforma, design detalhado e
contratos. Depois: grafo do agente, UX/integration validation ou runtime.
Saídas: mocks, pesquisa de API, validação de contrato, código de integração,
decisão de publicação, ferramentas publicadas, relatório e review. Só avance
quando o gate de publicação e a revisão estiverem aprovados.

### 5.8 quality-engineering-planning

**Propósito.** Produzir estratégia de testes, master test plan e cenários E2E
de alto nível.

~~~json
{
  "input_folder": "$PROJECT_DIR/artifacts/inputs",
  "output_folder": "$PROJECT_DIR/artifacts/outputs/quality-engineering-planning",
  "project_name": "project",
  "prd_path": "$PROJECT_DIR/artifacts/outputs/product-definition/prd",
  "epics_path": "$PROJECT_DIR/artifacts/outputs/product-definition/epics",
  "domain_boundaries_path": "$PROJECT_DIR/artifacts/outputs/software-architecture/domain-boundaries",
  "adrs_path": "$PROJECT_DIR/artifacts/outputs/software-architecture/adrs",
  "target_architecture_path": "$PROJECT_DIR/artifacts/outputs/software-architecture/target-architecture",
  "user_stories_path": "$PROJECT_DIR/artifacts/outputs/product-delivery/user-stories",
  "test_strategy_path": "$PROJECT_DIR/artifacts/outputs/quality-engineering-planning/qa-test-strategy",
  "master_test_plan_path": "$PROJECT_DIR/artifacts/outputs/quality-engineering-planning/qa-master-test-plan",
  "e2e_tc_path": "$PROJECT_DIR/artifacts/outputs/quality-engineering-planning/e2e-test-cases",
  "criteria_base_path": "$PROJECT_DIR/criteria"
}
~~~

**Melhores ligações.** Produto + arquitetura + histórias → QE planning →
<code>quality-engineering-design</code>. A automação web pode ser adicionada
depois; ela não está entre os 13 nós, embora seja referenciada pelo runtime no
JSON atual.

### 5.9 quality-engineering-design

**Propósito.** Derivar casos funcionais por história, normalmente em Gherkin,
cobrindo sucesso, erro e limites.

~~~json
{
  "input_folder": "$PROJECT_DIR/artifacts/inputs",
  "output_folder": "$PROJECT_DIR/artifacts/outputs/quality-engineering-design",
  "feature_id": "$.title",
  "project_name": "project",
  "prd_path": "$PROJECT_DIR/artifacts/outputs/product-definition/prd",
  "epics_path": "$PROJECT_DIR/artifacts/outputs/product-definition/epics",
  "adrs_path": "$PROJECT_DIR/artifacts/outputs/software-architecture/adrs",
  "user_stories_path": "$PROJECT_DIR/artifacts/outputs/product-delivery/user-stories",
  "test_strategy_path": "$PROJECT_DIR/artifacts/outputs/quality-engineering-planning/qa-test-strategy",
  "master_test_plan_path": "$PROJECT_DIR/artifacts/outputs/quality-engineering-planning/qa-master-test-plan",
  "failure_feedback": "",
  "test_cases_output_folder": "test-cases",
  "test_cases_path": "$PROJECT_DIR/artifacts/outputs/quality-engineering-design/test-cases"
}
~~~

**Melhores ligações.** Entrada: histórias, ADRs, estratégia e master plan.
Saída: <code>test_cases_path</code>, consumível por desenvolvimento, automação
ou runtime. Para evitar mistura de evidências, use uma pasta por feature/épico.

### 5.10 product-definition

**Propósito.** Transformar briefing, entrevistas e legado em PRD e épicos
validados. É a porta de entrada do fluxo completo; não é obrigatório no quick
lane já bem definido.

~~~json
{
  "input_folder": "$PROJECT_DIR/artifacts/inputs",
  "output_folder": "$PROJECT_DIR/artifacts/outputs/product-definition",
  "project_brief": "$PROJECT_DIR/docs/product-briefing-java.md",
  "project_name": "project",
  "meeting_recording": "$PROJECT_DIR/meetings",
  "transcript_output": "$PROJECT_DIR/artifacts/inputs/transcripts",
  "prd_template": "$PROJECT_DIR/artifacts/inputs/prd_template.md",
  "legacy_docs_path": "$PROJECT_DIR/artifacts/outputs/legacy-insights",
  "epics_output_path": "$PROJECT_DIR/artifacts/outputs/product-definition/epics",
  "prd_output_path": "$PROJECT_DIR/artifacts/outputs/product-definition/prd",
  "quality_criteria_path": "$PROJECT_DIR/criteria/prd-criteria.md"
}
~~~

**Melhores ligações.** Suas saídas
<code>prd_output_path</code> e <code>epics_output_path</code> alimentam
<code>software-architecture</code>, <code>product-delivery</code> e QE. O canvas
atual usa <code>project-brief.md</code> e critério de runtime; para uma execução
de produto, use o briefing real e critérios próprios de PRD/épico.

### 5.11 product-delivery

**Propósito.** Transformar PRD/épicos em histórias de usuário detalhadas,
critérios de aceitação, matriz técnica e export para plataforma. Também pode
verificar conformidade com a arquitetura.

~~~json
{
  "project_name": "project",
  "delivery_platform": "csv-file",
  "servicenow_hierarchy_mode": "epic_story",
  "export_scope": "all",
  "selected_epics": "",
  "selected_stories": "",
  "input_folder": "$PROJECT_DIR/artifacts/inputs",
  "output_folder": "$PROJECT_DIR/artifacts/outputs/product-delivery",
  "feature_id": "$.title",
  "epics_input_path": "$PROJECT_DIR/artifacts/outputs/product-definition/epics",
  "prd_input_path": "$PROJECT_DIR/artifacts/outputs/product-definition/prd",
  "target_architecture_input_path": "$PROJECT_DIR/artifacts/outputs/software-architecture/target-architecture",
  "adr_input_path": "$PROJECT_DIR/artifacts/outputs/software-architecture/adrs",
  "dtr_input_path": "$PROJECT_DIR/artifacts/outputs/software-architecture/dtr",
  "user_stories_output_folder": "user-stories",
  "user_stories_output_path": "$PROJECT_DIR/artifacts/outputs/product-delivery/user-stories",
  "platform_export_output_folder": "platform-export",
  "platform_export_output_path": "$PROJECT_DIR/artifacts/outputs/product-delivery/platform-export",
  "compliance_output_folder": "architecture-compliance",
  "compliance_output_path": "$PROJECT_DIR/artifacts/outputs/product-delivery/architecture-compliance",
  "story_scope": "all",
  "quality_criteria_path": "$PROJECT_DIR/criteria/stories-criteria.md"
}
~~~

**Melhores ligações.** Entrada: PRD e épicos; contexto: arquitetura, ADRs e
DTR; saída: <code>user_stories_output_path</code> para sprint, QE e
desenvolvimento e <code>platform_export_output_path</code> para a plataforma
escolhida. Para uma única feature, prefira <code>export_scope: "selected"</code>
e selecione histórias.

### 5.12 software-architecture

**Propósito.** Descobrir bounded contexts, gerar ADRs, estabelecer arquitetura-
alvo, detalhar tecnologia e produzir o DTR que ajuda o runtime a identificar
como iniciar a aplicação.

~~~json
{
  "input_folder": "$PROJECT_DIR/artifacts/inputs",
  "output_folder": "$PROJECT_DIR/artifacts/outputs/software-architecture",
  "project_name": "project",
  "current_architecture": "$PROJECT_DIR/docs/current-architecture.md",
  "technical_interview": "$PROJECT_DIR/artifacts/inputs/transcripts/tech-transcript.md",
  "meeting_recording": "$PROJECT_DIR/meetings",
  "prd_path": "$PROJECT_DIR/artifacts/outputs/product-definition/prd",
  "epics_path": "$PROJECT_DIR/artifacts/outputs/product-definition/epics",
  "domain_boundaries": "domain-boundaries",
  "adrs": "adrs",
  "tech_stack": "tech-stack",
  "target_architecture": "$PROJECT_DIR/artifacts/outputs/software-architecture/target-architecture",
  "dtr_mode": "brownfield",
  "project_brief_path": "$PROJECT_DIR/docs/product-briefing-java.md",
  "dtr_source_path": "$PROJECT_DIR/source",
  "dtr": "$PROJECT_DIR/artifacts/outputs/software-architecture/dtr",
  "derive_validation_tools": true,
  "validation_tools_output_path": "$PROJECT_DIR/context-pack"
}
~~~

**Melhores ligações.** Entrada: PRD/épicos; saídas:
<code>domain_boundaries_path</code>, <code>adrs_path</code>,
<code>target_architecture_path</code>, <code>dtr_path</code> e
<code>validation_tools_path</code>. Consumidores: delivery, QE, desenvolvimento
e runtime. Use <code>greenfield</code> para produto novo e
<code>brownfield</code> para o projeto existente.

### 5.13 software-architecture-autoloop

**Propósito.** Variante de arquitetura com verificações automáticas de bounded
contexts, ADRs, fundação, especificação e DTR, produzindo veredictos e
relatórios de conformidade.

**Status do perfil.** O nome aparece no JSON da playlist, mas não aparece como
YAML de capability no perfil local nem como entrada equivalente no catálogo
local consultado. Valide a versão instalada antes de usar.

~~~json
{
  "input_folder": "$PROJECT_DIR/artifacts/inputs",
  "output_folder": "$PROJECT_DIR/artifacts/outputs/software-architecture-autoloop",
  "project_name": "project",
  "current_architecture": "$PROJECT_DIR/docs/current-architecture.md",
  "technical_interview": "$PROJECT_DIR/artifacts/inputs/transcripts/tech-transcript.md",
  "meeting_recording": "$PROJECT_DIR/meetings",
  "prd_path": "$PROJECT_DIR/artifacts/outputs/product-definition/prd",
  "epics_path": "$PROJECT_DIR/artifacts/outputs/product-definition/epics",
  "domain_boundaries": "$PROJECT_DIR/artifacts/outputs/software-architecture-autoloop/domain-boundaries",
  "adrs": "$PROJECT_DIR/artifacts/outputs/software-architecture-autoloop/adrs",
  "tech_stack": "tech-stack",
  "target_architecture": "$PROJECT_DIR/artifacts/outputs/software-architecture-autoloop/target-architecture",
  "dtr_mode": "brownfield",
  "project_brief_path": "$PROJECT_DIR/docs/product-briefing-java.md",
  "dtr_source_path": "$PROJECT_DIR/source",
  "dtr": "$PROJECT_DIR/artifacts/outputs/software-architecture-autoloop/dtr",
  "derive_validation_tools": true,
  "validation_tools_output_path": "$PROJECT_DIR/artifacts/outputs/software-architecture-autoloop/context-pack"
}
~~~

Use esta capability no lugar da arquitetura comum ou isole completamente seus
outputs. Não deixe as duas competirem pelo mesmo PRD/ADRs/target architecture.
Os veredictos de bounded context, ADR, foundation, specification e DTR devem
liberar os consumidores apenas quando estiverem aprovados.

## 6. Conexões recomendadas

| De | Artefato/estado | Para | Condição |
|---|---|---|---|
| <code>product-definition</code> | PRD e épicos | arquitetura/delivery | Gate do produto aprovado. |
| <code>software-architecture</code> | target, ADRs, DTR | delivery, QE, código, runtime | Arquitetura validada. |
| <code>product-delivery</code> | user stories | sprint, QE, código | Histórias prontas. |
| <code>quality-engineering-planning</code> | estratégia/master plan | QE design | Gates de QE aprovados. |
| <code>quality-engineering-design</code> | test cases | código/automação | Casos disponíveis para a fatia. |
| <code>sprint-planning</code> | sub-goal decomposition | grupo iterativo | Fila validada. |
| <code>quick-story-definition</code> | quick story | quick change | <code>story_readiness == "READY_FOR_QUICK_CHANGE"</code>. |
| <code>quick-change-implementation</code> | source/apply verdict | runtime | Aplicação aceita. |
| <code>code-development-autoloop</code> | source/review status | runtime | <code>review_status == "PASSED"</code>. |
| <code>local-runtime-validation</code> | feedback de runtime | reparo de código | Runtime falhou; preservar evidência. |
| <code>static-security-analysis</code> | findings/grafo/status | triagem/reparo | Intake autorizado e scan concluído. |
| <code>mcp-tools-development</code> | contratos/publicação | grafo/integração/runtime | Gate de publicação aprovado. |

## 7. Playlists viáveis

### Playlist A — Quick Small Feature enxuta

**Objetivo:** uma pequena mudança, localizada e runtime-validada.

~~~text
quick-story-definition
        │ READY_FOR_QUICK_CHANGE
        ▼
quick-change-implementation
        │ APPLIED_VERIFIED ou APPLIED_UNVERIFIED
        ▼
local-runtime-validation
~~~

**Capabilities e configurações indispensáveis:**

| Ordem | Capability | Configuração |
|---:|---|---|
| 1 | <code>quick-story-definition</code> | <code>story_type: feature</code>, request real, <code>feature_id: $.title</code>, source real. |
| 2 | <code>quick-change-implementation</code> | <code>quick_story_path</code> = saída da etapa 1, mesmo <code>source_path</code>, <code>skip_runtime_validation: false</code>. |
| 3 | <code>local-runtime-validation</code> | source atualizado, smoke <code>auto</code>, banco <code>auto</code>, limpeza ligada. |

### Playlist B — Quick Small Feature em fila

**Objetivo:** várias mudanças pequenas, uma por iteração.

~~~text
sprint-planning
      │ SUB-GOAL-DECOMPOSITION
      ▼
grupo Small Feature Implementation
  quick-story-definition → quick-change-implementation
      │ item aplicado
      ▼
local-runtime-validation
~~~

Use <code>chunking_criteria: quickchange-scope-tripwire</code>,
<code>max_sub_goals: 20</code> como ponto inicial,
<code>loop: true</code> e <code>loop_source_artifact:
sub_goal_decomposition_path</code>. O iterator deve transportar apenas o título,
descrição, requisitos e identificador do item atual.

Esta é a composição mais próxima da tela. Os demais nós podem permanecer como
referências visuais, mas não precisam estar no caminho executado.

### Playlist C — Escalonamento quick lane → full lane

**Objetivo:** começar pequeno e escalar somente quando a história exigir.

~~~text
quick-story-definition
 ├─ READY_FOR_QUICK_CHANGE -> quick-change-implementation -> runtime
 ├─ READY_FOR_PRODUCT_DEFINITION -> product-definition -> full lane
 ├─ TRIAGE/BLOCKED -> gate humano
 └─ FIX -> rota de correção
~~~

A condição central é <code>story_readiness</code>. Não use apenas uma mensagem
textual para simular roteamento; registre as condições no DAG.

### Playlist D — Feature completa da definição ao runtime

**Objetivo:** feature média/alta com rastreabilidade de produto, arquitetura,
qualidade, código e execução.

~~~text
product-definition
      ├──────────────> software-architecture
      └──────────────> product-delivery
                              └──> user stories
software-architecture ───────> delivery / QE / code
product-delivery ─────────────> sprint-planning
QE planning ──────────────────> QE design
sprint-planning ──────────────> loop(code-development-autoloop -> runtime)
~~~

Ordem sugerida:

1. <code>product-definition</code> produz PRD/épicos;
2. <code>software-architecture</code> ou
   <code>software-architecture-autoloop</code> produz arquitetura/ADRs/DTR;
3. <code>product-delivery</code> produz histórias;
4. <code>quality-engineering-planning</code> produz estratégia e master plan;
5. <code>quality-engineering-design</code> produz casos;
6. <code>sprint-planning</code> cria a fila;
7. <code>code-development-autoloop</code> implementa uma fatia;
8. <code>local-runtime-validation</code> prova a execução.

### Playlist E — Qualidade primeiro, sem implementação

**Objetivo:** preparar estratégia e casos antes de escrever código.

~~~text
product-definition -> software-architecture -> product-delivery
                                      -> quality-engineering-planning
                                      -> quality-engineering-design
~~~

Use em projetos regulados ou features críticas. Adicione
<code>quality-engineering-web-automation</code> depois dos casos se for
necessário descobrir seletores e executar browser. Essa capability não está nos
13 nós da imagem.

### Playlist F — Segurança antes da entrega

**Objetivo:** analisar código autorizado, decidir sobre findings e só então
implementar/remediar.

~~~text
product-definition -> software-architecture -> product-delivery
software-architecture -> static-security-analysis
static-security-analysis -> triagem/gate
gate aprovado -> code-development-autoloop -> local-runtime-validation
~~~

<code>static-security-analysis</code> deve receber intake e escopo autorizados.
Findings brutos devem passar por triagem antes de virar uma tarefa. Para
remediação, prefira <code>scope_type: bug-fixing</code> no autoloop.

### Playlist G — Solução agentic com MCP

**Objetivo:** construir ferramentas MCP e integrá-las ao código/runtime.

~~~text
product-definition -> software-architecture-autoloop
                              ├-> mcp-tools-development
                              └-> code-development-autoloop
                                      -> local-runtime-validation
~~~

Preencha design detalhado, blueprint de plataforma e contratos de API no MCP.
Para uma solução agentic completa, normalmente ainda serão necessárias
capabilities de grafo, UX e validação de integração, que não estão entre os 13
nós.

## 8. Grupo iterativo

O grupo registrado na playlist é:

~~~json
{
  "id": "group",
  "display_name": "Small Feature Implementation",
  "loop": true,
  "loop_source_artifact": "sub_goal_decomposition_path",
  "capabilities": [
    "quick-story-definition",
    "quick-change-implementation"
  ],
  "iterator_param_map": {}
}
~~~

Se a herança automática não existir na versão do executor, configure o iterator
para transportar:

~~~json
{
  "feature_id": "$.title",
  "request_path": "$.request_path",
  "description": "$.description",
  "requirements": "$.requirements"
}
~~~

Para uma fila de features completas, use outro grupo:

~~~json
{
  "id": "feature-development-cycle",
  "display_name": "Feature Slice to Runtime-Validated Code",
  "loop": true,
  "loop_source_artifact": "sub_goal_decomposition_path",
  "capabilities": [
    "code-development-autoloop",
    "local-runtime-validation"
  ],
  "iterator_param_map": {}
}
~~~

Não misture quick change e code-development-autoloop no mesmo item sem
roteamento por condição: são lanes de implementação alternativas.

## 9. Checklist de execução

### Entrada e registry

- [ ] <code>project_name</code> está definido.
- [ ] Existe um <code>source_path</code> real e único.
- [ ] O pedido possui título, descrição e requisitos quando usa referências
      <code>$.title</code>/<code>$.description</code>/<code>$.requirements</code>.
- [ ] PRD, épicos e histórias têm uma fonte oficial.
- [ ] Cada capability escolhida possui YAML/contrato no registry.
- [ ] Cada skill referenciada está instalada.
- [ ] A versão do Stepwise aceita grupos, sinais e condições usados.

### DAG

- [ ] Existe caminho do nó inicial até cada nó que será executado.
- [ ] Toda entrada obrigatória possui produtor explícito.
- [ ] Sucesso e falha possuem rotas diferentes.
- [ ] Não há dois produtores gravando o mesmo caminho sem intenção.
- [ ] Só uma capability de arquitetura é produtora oficial.
- [ ] O grupo recebe a fila e inicia no primeiro membro.

### Runtime e segurança

- [ ] O contrato de autorização existe antes da análise de segurança.
- [ ] Segredos não estão escritos na playlist.
- [ ] <code>cleanup_services</code> permanece <code>true</code>, salvo debug.
- [ ] Banco, targets, rotas, timeout e viewports combinam com o projeto.
- [ ] Findings são triados antes de virar correção.
- [ ] Feedback de runtime/review é preservado para reparos.

## 10. Recomendação final

Para o objetivo declarado pelo nome **Loop Quick Small Feature**, a playlist
executável recomendada é:

~~~text
[sprint-planning, opcional]
        ▼
grupo Small Feature Implementation
  quick-story-definition
        ▼ READY_FOR_QUICK_CHANGE
  quick-change-implementation
        ▼ APPLIED_VERIFIED / APPLIED_UNVERIFIED
local-runtime-validation
~~~

As demais capabilities devem permanecer disponíveis como referência ou ser
montadas em playlists especializadas. A divisão natural é:

- produto: <code>product-definition</code> e <code>product-delivery</code>;
- arquitetura: <code>software-architecture</code> ou
  <code>software-architecture-autoloop</code>;
- qualidade: <code>quality-engineering-planning</code> e
  <code>quality-engineering-design</code>;
- segurança: <code>static-security-analysis</code> + triagem;
- lane completa: <code>code-development-autoloop</code>;
- agentic: <code>mcp-tools-development</code> + grafo/UX/integração;
- evidência de execução: <code>local-runtime-validation</code>.

## 11. Referências locais

- [JSON da playlist Loop Quick Small Feature](../artifacts/outputs/playlist/loop-quick-small-feature-agent-guide.json)
- [Playlist de entrega iterativa de arquitetura](../artifacts/outputs/playlist/software-architecture-story-iterative-agent-guide.json)
- [Registry instalado no perfil Stepwise](../artifacts/outputs/stepwise-story-iterative-profile/registry/)
- [Briefing do projeto](product-briefing-java.md)

O JSON salvo no projeto continua sendo a fonte da configuração atual. Este
guia fornece as composições e os valores recomendados; o contrato efetivamente
instalado no registry e os enums da versão do Stepwise prevalecem antes do Play.

