# AI PROJECT STATE

## Current Phase

Fase 7 — Pré-deploy comercial concluído em código

## Status

CÓDIGO COMERCIAL CONSOLIDADO; DEPLOY REAL BLOQUEADO APENAS POR CONFIGURAÇÃO EXTERNA DE INFRAESTRUTURA

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

## Produção

O `render.yaml` está preparado para:
- API FastAPI;
- frontend React estático;
- cron de lembretes;
- secrets de MongoDB/OpenAI/Stripe/WhatsApp;
- automação de custom domains via API do Render.

Render documenta web/static/cron services em Blueprints e custom domains por serviço; a API também permite criar/verificar/remover custom domains. citeturn830529search1turn830529search0turn830529search6

## Validação

O workflow de CI foi configurado para pull requests, com cancelamento de execuções obsoletas.

No momento do checkpoint, o GitHub Actions estava mantendo o último workflow em fila e o commit não apresentava status de falha. Isso é uma limitação do runner externo, não uma confirmação de teste verde.

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

Código consolidado na branch `feature/ai-phase-3.2` e preparado para merge/produção.

Após conectar a infraestrutura externa:
1. aplicar `render.yaml`;
2. preencher secrets;
3. deploy;
4. smoke test;
5. conectar primeiro domínio;
6. executar E2E com cliente real.

## Timestamp

2026-09-18
