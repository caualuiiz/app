# Gestão SaaS — PRD

## Fases concluídas
- **Fase 1** — Auth JWT + multi-tenant + Company + Object Storage
- **Fase 2** — Agenda/Clientes/Serviços/Disponibilidade/Agendamentos + Dashboard
- **Fase 3** — Landing pública `/{slug}` + IA construtora com preview em tempo real
- **Fase 3+** (13/02/2026) — 4 melhorias:
  - **Agendamento público** `/{slug}/agendar` reutilizando validação de conflito da Fase 2; auto-cria cliente por telefone; agendamento entra em `PENDING` na agenda administrativa
  - **Análise de fotos com IA** (`POST /landing/me/analyze-gallery`) usando vision (base64 → GPT-4o-mini) para sugerir cor primária, tema, textos e diferenciais reais das imagens
  - **Editor visual** ao lado do chat: pickers de cor primária/secundária, toggles de todas as seções, escolha da imagem principal do hero; salva via `PUT /landing/me/state`
  - **Comandos rápidos**: chips clicáveis no chat com sugestões dinâmicas retornadas pela IA a cada resposta + fallback de comandos padrão

## Endpoints novos
- `GET /api/public/{slug}/booking-context` — serviços + profissionais + horas
- `GET /api/public/{slug}/slots?service_id&professional_id&date` — slots livres
- `POST /api/public/{slug}/book` — criar agendamento público
- `POST /api/landing/me/analyze-gallery` — vision analysis
- `DELETE /api/landing/me/gallery/{item_id}` — remover foto

## Multi-tenancy
- Booking valida `slug + is_published`, resolve `company_id`, cria cliente/appointment com esse company_id
- Análise de imagens só lê arquivos com `files.company_id == membership.company_id`
- Todas as regras da Fase 2 (`_validate_slot`) reaproveitadas

## Backlog
- Fase 4 — Notificações (Resend + WhatsApp) confirmando bookings públicos
- Fase 5 — Financeiro completo (comandas, comissões, fluxo de caixa)
- Fase 6 — Relatórios avançados
- Fase 7 — Planos, assinaturas, painel admin do SaaS
