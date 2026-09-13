# Gestão SaaS — PRD

## Fase 1 (concluída em 11/02/2026)
- Auth JWT (bcrypt + cookies httpOnly), registro/login/logout/refresh/forgot(log)/reset
- Multi-tenant via memberships (OWNER/MANAGER/PROFESSIONAL); backend valida sempre
- Onboarding, dashboard, empresa (uploads via Emergent Object Storage), gestão de membros
- Isolamento validado com 2 tenants (403 em cross-tenant)

## Fase 2 — Agenda e agendamentos (concluída 13/02/2026)
- **Clientes**: CRUD + pesquisa + histórico (`/api/clients`), escopo por tenant
- **Serviços**: CRUD com duração/preço/ativação + vínculo com profissionais (`/api/services`)
- **Disponibilidade**: horários da empresa e por profissional com almoço (`/api/availability/...`)
- **Agendamentos**: CRUD + validação de conflito, horário de funcionamento, dia inativo, almoço; cancelar libera slot; PROFESSIONAL só vê/altera os próprios (`/api/appointments`)
- **Dashboard**: contadores por status + faturamento previsto + próximos atendimentos (`/api/dashboard/summary`)
- **Frontend**: Agenda com visão Dia/Semana/Mês, navegação, modal criar/detalhar, badges por status
- **Índices Mongo** adicionados; snapshot de nome/preço nos agendamentos

## Backlog próximas fases
- FASE 3 — Página pública de agendamento (usa slug + services + disponibilidade)
- FASE 4 — Notificações (Resend/WhatsApp) para confirmações
- FASE 5 — Financeiro completo, comissões, comandas
- FASE 6 — Relatórios avançados
- FASE 7 — Planos, assinaturas, painel admin do SaaS
