# AI PROJECT STATE

## Current Phase

Fase 8 — Hardening concluído; preparação de produção concluída em código

## Status

CÓDIGO COMERCIAL CONSOLIDADO; HARDENING E PREPARAÇÃO DE PRODUÇÃO CONCLUÍDOS EM CÓDIGO

## Núcleo

O produto possui um Landing Brain com experiência fixa de 20+ anos:
**Diretor de Arte Digital + Especialista em Landing Pages.**

A especificação canônica do nível máximo do agente está em `SENIOR_AGENT_SPEC.md`.
A taxonomia interna é: **Júnior → Pleno → Avançado → Sênior**, sendo **Sênior o nível máximo do produto**.

Importante: a especificação define o padrão-alvo e os critérios de certificação; ela não significa que todas as capacidades já estejam certificadas.

O agente não aprende com clientes. Analisa os dados de cada negócio e decide como usar fotos, referências, identidade visual, estrutura e conversão.

## Pipeline

`Dados → Visual Intelligence → Landing Brain → Landing Blueprint → Render Specification → Preview → Autocrítica → Refinamento → Apply/Publish`

## Entregas concluídas

- SaaS multi-tenant, agenda, clientes, serviços e booking público.
- Landing pública e editor.
- Visual Intelligence com análise por imagem.
- Reference Intelligence.
- Art Direction.
- Design System.
- Layout Plan.
- Render Specification.
- Preview/Apply.
- Landing Brain profissional.
- Blueprint com posicionamento de mídia.
- Autocrítica e refinamento automático.
- Publicação condicionada à crítica aprovada.
- OpenAI Responses API como motor de execução.
- WhatsApp Cloud API, múltiplos números, aprovação/recusa e lembretes.
- Stripe Checkout, Portal, webhook e limites server-side.
- Domínio personalizado com verificação e integração com Render Custom Domains.
- Booking e landing em domínio personalizado.
- Rotação/revogação de refresh sessions.
- Access token reduzido para 30 minutos.
- Remoção de armazenamento de senha temporária em texto.
- CI para backend/frontend.
- Blueprint Render para API, frontend e cron.
- Nenhuma chave real versionada.
- Uploads migrados para MongoDB GridFS, sem dependência obrigatória do storage legado Emergent.
- Compatibilidade de leitura legada preservada quando `EMERGENT_LLM_KEY` estiver presente durante a migração.
- CI verde anteriormente no commit `801dcfa825ec941cd1b593e9c3a57a02ba1f176` (backend + frontend).
- Workflow de CI limpo, sem diagnóstico temporário de AJV.
- Render frontend corrigido com `rootDir: frontend` e `staticPublishPath: build`.
- Render configurado com `ENVIRONMENT=production` e `WHATSAPP_APP_SECRET`.
- CORS de produção exige `FRONTEND_URL` e não utiliza wildcard.
- Health check retorna HTTP 503 quando o MongoDB está indisponível.
- Login agora persiste refresh sessions; refresh continua com rotação e revogação.
- Reset tokens de senha são armazenados apenas como hash e sessões de refresh são invalidadas após troca de senha.
- Dependência de bootstrap do storage legado removida do servidor.
- Runbook de deploy e critérios de aceite adicionados em `PRODUCTION_RUNBOOK.md`.
- CI confirmado verde no run `35332531375`: backend e frontend `success`.

## Produção

O `render.yaml` está preparado para:
- API FastAPI;
- frontend React estático;
- cron de lembretes;
- secrets de MongoDB/OpenAI/Stripe/WhatsApp;
- automação de custom domains via API do Render.

Render documenta web/static/cron services em Blueprints e custom domains por serviço; a API também permite criar/verificar/remover custom domains. citeturn830529search1turn830529search0turn830529search6

## Validação

O workflow de CI executa backend e frontend em pushes/PRs para `main`, com cancelamento de execuções obsoletas.

Última validação confirmada: run `35308757341`, commit `801dcfa825ec941cd1b593e9c3a57a02ba1f176`, backend `success`, frontend `success`.

## Deploy real

Ainda depende de credenciais/contas externas:
- MongoDB;
- OpenAI API key;
- Stripe;
- Meta WhatsApp;
- Render/AppDeploy;
- DNS do domínio real.

Esses segredos não são armazenados no GitHub.

## Senior Level

`SENIOR_AGENT_SPEC.md` foi adicionado como referência oficial para arquitetura, comportamento, segurança, UX/UI, conversão, acessibilidade, SEO, performance, autocrítica, refinamento, testes e critérios de certificação do agente.

Estado atual: **ESPECIFICAÇÃO SENIOR DEFINIDA; IMPLEMENTAÇÃO/CERTIFICAÇÃO CONTINUAM DEPENDENTES DE AUDITORIA POR REQUISITO**.

## Current Pause Point

A `main` está com o hardening de produção aplicado, CI verde confirmado, o storage de uploads já não depende do serviço legado, e a especificação formal do Agente Landing AI — Senior Level está registrada no projeto.

Próximos passos técnicos:
1. aplicar `render.yaml` no Render;
2. preencher secrets externos;
3. deploy;
4. smoke test de API/frontend;
5. configurar Stripe/WhatsApp/OpenAI;
6. conectar primeiro domínio;
7. executar E2E com cliente real;
8. auditar a implementação contra `SENIOR_AGENT_SPEC.md` e marcar cada requisito como NOT_STARTED, PARTIAL, IMPLEMENTED, HARDENED, SENIOR_READY ou SENIOR_CERTIFIED.

As etapas que dependem de contas externas (Render/MongoDB/Stripe/Meta/DNS) permanecem fora do GitHub até que essas conexões sejam disponibilizadas.

## Timestamp

2026-09-18

## Senior Spec Timestamp

2026-09-18 — `SENIOR_AGENT_SPEC.md` adicionado ao repositório como especificação canônica.
