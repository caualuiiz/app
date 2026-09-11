# Gestão SaaS — Fase 1 (Fundação Multi-Tenant)

## Problema original
Construir a fundação de um SaaS multi-tenant profissional de gestão e agendamento para
pequenos negócios de serviços (barbearias, salões, manicures, estética, pet shops).
Fase 1 = SOMENTE fundação: auth, empresas, permissões, isolamento entre tenants.
Nenhuma funcionalidade das fases 2–8 deve ser implementada.

## Arquitetura
- **Stack**: FastAPI + MongoDB (Motor) + React (CRA) + Tailwind + shadcn/ui + sonner
- **Auth**: JWT customizado (bcrypt + PyJWT, cookies httpOnly SameSite=None+Secure, 24h access + 7d refresh)
- **Storage**: Emergent Object Storage (`INTEGRATION_PROXY_URL` + `EMERGENT_LLM_KEY`) para logo e foto
- **Multi-tenant**: coleção `memberships` (user_id + company_id + role). O header `X-Company-Id` é apenas hint — o backend SEMPRE valida a membership real via query. Toda rota de tenant é filtrada por `membership["company_id"]`.
- **Papéis**: OWNER, MANAGER, PROFESSIONAL

## Personas
- **OWNER**: proprietário; único que pode alterar nome da empresa, gerenciar membros e trocar papéis.
- **MANAGER**: pode ver e editar configurações (exceto nome) e listar membros.
- **PROFESSIONAL**: acesso limitado ao painel (permissões expansíveis nas próximas fases).

## Requisitos entregues (11/02/2026)
- Cadastro, login, logout, refresh, forgot-password (log), reset-password
- Onboarding (criação de empresa + business_type + auto-OWNER)
- Dashboard com greeting + 5 cards "Em breve" + atalhos para OWNER/MANAGER
- Configurações da empresa (todos os campos + upload de logo/foto via Object Storage)
- Gestão de membros (adicionar, trocar papel, remover)
- Sidebar + header responsivos com menu do usuário
- Rate-limit de brute force (5 tentativas → lock 15min)
- Índices unique em `users.email`, `companies.slug`, `memberships(user_id, company_id)`

## Isolamento multi-tenant testado
- 2 tenants criados; Owner B tentou ler e alterar dados do Owner A enviando `X-Company-Id` forjado — todos os endpoints retornaram 403.
- Owner B não vê memberships do tenant A.

## Configuração externa
- Nenhuma. `EMERGENT_LLM_KEY` é gerenciada pela plataforma; `INTEGRATION_PROXY_URL` já disponível.
- Recuperação de senha por e-mail (Resend) foi propositalmente deixada preparada mas sem envio real — o link é logado no console (definição do usuário para Fase 1).

## Backlog para próximas fases
- FASE 2 — Configuração completa da empresa (horários, redes sociais, bandeira visual própria)
- FASE 3 — Serviços e profissionais
- FASE 4 — Agenda / calendário
- FASE 5 — Clientes (CRM)
- FASE 6 — Página pública de agendamento (usa o slug já gerado)
- FASE 7 — Dashboard e relatórios
- FASE 8 — Planos, assinaturas, pagamentos e painel admin do SaaS
