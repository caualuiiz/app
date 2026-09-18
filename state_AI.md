# AI PROJECT STATE

## Current Phase

Fase 8 — Hardening de produção e preparação de deploy

## Status

CÓDIGO COMERCIAL CONSOLIDADO; HARDENING DE PRODUÇÃO EM ANDAMENTO

## Núcleo

O produto possui um Landing Brain com experiência fixa de 20+ anos:
**Diretor de Arte Digital + Especialista em Landing Pages.**

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
- CI verde no commit `801dcfa825ec941cd1b593e9c3a57a02ba1f176` (backend + frontend).

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

## Current Pause Point

A `main` está validada pelo CI e o storage de uploads já não depende do serviço legado.

Próximos passos técnicos:
1. aplicar `render.yaml` no Render;
2. preencher secrets externos;
3. deploy;
4. smoke test de API/frontend;
5. configurar Stripe/WhatsApp/OpenAI;
6. conectar primeiro domínio;
7. executar E2E com cliente real.

## Timestamp

2026-09-18
