# Gestão SaaS — PRD

## Fases concluídas
- **Fase 1** (11/02/2026) — Auth JWT + multi-tenant + memberships + Company settings + Object Storage
- **Fase 2** (13/02/2026) — Agenda/Clientes/Serviços/Disponibilidade/Agendamentos + validação de conflito + Dashboard real
- **Fase 3** (13/02/2026) — Landing Page pública `/{slug}` + IA construtora conversacional (GPT-4o-mini via emergentintegrations) com preview em tempo real, upload de galeria, publicação, persistência

## Endpoints Fase 3
- `GET /api/landing/me` — carrega state + mensagens (auto-cria)
- `POST /api/landing/me/chat` — IA responde e devolve state atualizado
- `POST /api/landing/me/gallery` — upload de foto para galeria
- `PUT /api/landing/me/state` — salvar state manualmente
- `POST /api/landing/me/publish` — publicar
- `GET /api/public/{slug}` — dados públicos da página
- `GET /api/public/uploads/{path}` — servir imagens públicas (verifica ownership via company_id)

## Multi-tenant
- Todas as rotas de landing usam `require_membership`; state e mensagens vinculados a `company_id`
- Rota pública valida `slug` + `is_published`; upload público via `files.company_id`

## Próximas fases sugeridas
- Fase 4 — Fluxo de agendamento público a partir da landing (`/{slug}/agendar`)
- Fase 5 — Notificações (Resend, WhatsApp)
- Fase 6 — Financeiro completo
- Fase 7 — Relatórios avançados + Painel admin do SaaS + Planos/assinaturas
