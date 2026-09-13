# Gestão SaaS — PRD

## Fases concluídas
- **Fase 1** — Auth JWT multi-tenant + Company + Object Storage
- **Fase 2** — Agenda, Clientes, Serviços, Disponibilidade, Agendamentos, Dashboard, conflitos, permissões
- **Fase 3** — Landing pública `/{slug}` + IA construtora com preview + análise de fotos + editor visual + comandos rápidos + agendamento público `/{slug}/agendar`
- **Fase 4** (13/02/2026) — **Assistente Operacional Inteligente**

## Novidades da Fase 4
### Backend
- `routes_assistant.py` com **13 ferramentas reais** executáveis pela IA:
  - `get_summary`, `list_appointments`, `list_services`, `create_service`, `update_service`, `list_clients`, `create_client`, `list_professionals`, `create_appointment`, `cancel_appointment`, `block_schedule`, `get_availability`, `update_landing`
- Cada tool reusa a lógica das fases 1-3 (mesma validação de conflito, snapshots, permissões por papel, tenant do membership)
- Loop de tool-calling manual (até 4 iterações) via LlmChat + GPT-4o-mini
- Coleções novas:
  - `schedule_blocks` (integrada ao `_validate_slot` da Fase 2 — bloqueio bloqueia agendamentos)
  - `assistant_sessions` (histórico por usuário/empresa, últimas 40 mensagens)
  - `assistant_audit` (registro de cada tool executada com args + resultado)
- Endpoints: `POST /api/assistant/chat`, `GET /api/assistant/history`, `POST /api/assistant/reset`

### Frontend
- `FloatingAssistant.jsx` — botão flutuante em toda área autenticada (via AppShell)
- Painel lateral (desktop) / tela cheia (mobile) com histórico, sugestões contextuais por rota, badges de tools executadas
- Sugestões dinâmicas retornadas pela IA + fallback contextual por rota (`/agenda`, `/clients`, `/services`, `/landing`, etc.)

## Comportamentos garantidos
- IA pede **confirmação antes de ações destrutivas** (block_schedule, cancelar em massa, etc.)
- Permissões: PROFESSIONAL vê só os próprios; MANAGER/OWNER conforme já configurado
- Nunca inventa dados: se falta info, chama tool ou pergunta ao usuário
- Nunca confia em company_id do frontend: usa sempre o membership autenticado
- Português-BR forte via system prompt

## Testes executados (13/02/2026)
- Login admin → chat → get_summary retornou dados reais
- Chat "cadastre João" → create_client executado, cliente na base
- Chat "adicione serviço Barba 30min R$25" → create_service executado
- Chat "bloqueie 2026-09-15 das 15h às 19h" → IA pediu confirmação (correto)
- Regressão Fase 1-3: login, agenda, landing pública, agendamento público continuam OK
- Isolamento: assistente usa `require_membership` — impossível operar em outra empresa

## Limitações reais
- Sem integração real WhatsApp (arquitetura preparada: campo `source`, coleção `assistant_audit`, endpoint `assistant_audit` pronto para futuras notificações)
- Reset por usuário (não global por empresa) — decisão de UX
- Tool-calling é sequencial (não paralelo) — suficiente para o escopo atual

## Backlog
- Fase 5 — Integração WhatsApp oficial (notificações + atendimento via IA)
- Fase 6 — Financeiro completo, comissões, comandas
- Fase 7 — Relatórios avançados
- Fase 8 — Planos, assinaturas, painel admin do SaaS
