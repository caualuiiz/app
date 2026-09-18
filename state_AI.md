# AI PROJECT STATE

## Current Phase

Fase 7 — Preparação para Deploy Comercial + Domínio Personalizado

## Status

IMPLEMENTAÇÃO COMERCIAL AVANÇADA NA BRANCH `feature/ai-phase-3.2`; PENDENTE VALIDAÇÃO E2E/CI E CONFIGURAÇÃO EXTERNA DE PRODUÇÃO

## Núcleo de IA

O agente é um profissional fixo de:
**Diretor de Arte Digital + Especialista em Landing Pages, 20+ anos.**

Ele não aprende com clientes. Os dados do cliente são matéria-prima para análise e execução.

## Pipeline de criação

`Dados → Visual Intelligence → Landing Brain → Landing Blueprint → Render Specification → Preview → Autocrítica → Refinamento → Apply/Publish`

O Landing Brain decide:
- função de cada foto;
- seção de destino;
- tratamento, crop e ponto focal;
- paleta e tipografia;
- hierarquia e composição;
- estrutura;
- estratégia de conversão.

## Implementado

- Landing Blueprint e Media Placement.
- Visual Image Insight por imagem.
- Media Binding seguro.
- Preview/Apply integrado ao Blueprint.
- Autocrítica estruturada da própria landing.
- Refinamento de Blueprint a partir da crítica.
- Publicação bloqueada quando a autocrítica reprova.
- Engine direto via OpenAI Responses API; removida dependência privada do Emergent e de Anthropic.
- CI GitHub para backend/frontend.
- Segurança de refresh sessions com rotação/revogação.
- Redução do access token para 30 minutos.
- Remoção de armazenamento de senha temporária em texto.
- WhatsApp Cloud API com múltiplos números de notificação.
- Confirmação/recusa por WhatsApp.
- Lembretes 24h/2h via cron.
- Planos TRIAL/STARTER/PRO e limites server-side.
- Stripe Checkout, Portal e webhook assinado.
- Tela comercial para plano, domínio e WhatsApp.
- Domínio personalizado com verificação TXT.
- Landing e agendamento funcionando em domínio personalizado.
- Blueprint Render com API, frontend e cron.
- Configuração de segredos via Render `sync: false`/secret generation; nenhum segredo versionado.

## Segurança

- Isolamento multi-tenant preservado.
- Contexto da IA sanitizado.
- Fotos precisam pertencer à empresa autorizada.
- Media bindings seguros.
- Webhook WhatsApp assinado.
- Webhook Stripe assinado.
- Domínios únicos e tenant-scoped.
- Refresh sessions armazenadas com hash e revogação.

## Infraestrutura

Render suporta web services, static sites e cron jobs em Blueprint YAML; custom domains podem ser adicionados aos web/static services e têm TLS gerenciado pelo Render. citeturn739394search0turn739394search1turn739394search2

## Validação atual

A branch está sob CI automático. As execuções estavam enfileiradas no momento do checkpoint; a validação final precisa considerar o commit mais recente.

## Bloqueios externos restantes

Para o deploy comercial real, ainda será necessário configurar no ambiente de produção:
- MongoDB;
- OPENAI_API_KEY;
- Stripe;
- Meta WhatsApp;
- credenciais/conta de hospedagem;
- DNS/domínio.

Esses valores não entram no GitHub.

## Current Pause Point

O código de produto comercial está implementado. O próximo passo é:
1. CI verde no commit final;
2. merge para `main`;
3. deploy em Render;
4. configuração das variáveis secretas;
5. domínio real;
6. smoke test de produção;
7. primeiro E2E com uma empresa real.

## Timestamp

2026-09-18
