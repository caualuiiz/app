# AI PROJECT STATE

## Current Phase

Fase 2.8 — Preview Application

## Status

IMPLEMENTED WITH LIMITATIONS

As Fases 2.1 a 2.8 possuem contratos e integrações incrementais. A Fase 2.8 cria Preview Sessions isoladas por empresa, vinculadas a uma Render Specification e a uma versão da landing, sem publicar ou alterar o Draft automaticamente.

## Implemented

As Fases 2.1 a 2.7 permanecem implementadas com seus contratos, serviços, persistência, renderer AI_SPEC/LEGACY e endpoints.

A Fase 2.8 adiciona `CreatePreviewRequest` e `PreviewResponse` com `preview_id`, `company_id`, `landing_version`, `render_spec`, `created_at`, `expires_at` e status `CREATED`, `ACTIVE`, `APPLIED`, `EXPIRED` ou `CANCELLED`.

A criação usa a Render Specification mais recente da empresa ou uma especificação solicitada explicitamente, sempre consultada com `company_id` autenticado. A sessão é criada como `ACTIVE`, com expiração configurável entre 5 minutos e 24 horas, padrão de 30 minutos.

A consulta e a listagem marcam sessões `ACTIVE` ou `CREATED` como `EXPIRED` quando o prazo termina. Sessões `APPLIED` ou `CANCELLED` não são alteradas automaticamente.

O serviço não toca em `landing_pages`, não altera `is_published`, não publica e não aplica mudanças ao Draft. A persistência é feita somente em `preview_sessions`. Um índice normal em `expires_at` foi criado para consultas; as sessões expiradas não são apagadas automaticamente, preservando histórico.

O Landing Builder recebeu uma ação explícita `Gerar Preview`. Ela cria a sessão e troca o renderer da prévia local para o `render_spec` retornado, sem publicar. O botão de publicação permanece separado.

## Files Created

- `backend/ai/preview_application.py`
- `backend/ai/preview_service.py`
- `tests/test_preview_application.py`

## Files Modified

- `backend/routes_design.py`
- `backend/db.py`
- `frontend/src/pages/LandingBuilder.jsx`
- `state_AI.md`

## Endpoints Added

- `POST /api/design/create-preview`
- `GET /api/design/preview/{preview_id}`
- `GET /api/design/previews`

Todos exigem membership ativa e papel `OWNER` ou `MANAGER`. O tenant é obtido da membership autenticada e não é aceito no payload.

## Database Changes

- Nova coleção lógica `preview_sessions`.
- Índice único em `preview_id`.
- Índice em `preview_sessions(company_id, created_at desc)`.
- Índice normal em `expires_at`, sem TTL destrutivo.
- Nenhuma migração destrutiva.
- Nenhuma alteração foi feita no MongoDB nesta sessão.

## Tests

- `python3 -m pytest -q`
- `python3 -m compileall -q backend tests`
- `CI=true npm test -- --watchAll=false --runInBand`
- `npm run build`
- Importação da aplicação FastAPI e verificação dos caminhos OpenAPI.
- `git diff --check`.

## Passed

- 34 testes backend cumulativos passaram.
- 3 testes frontend passaram.
- Expiração converte `ACTIVE` para `EXPIRED`.
- Expiração não altera `APPLIED`.
- Expiração tem limites entre 5 minutos e 24 horas.
- Contrato rejeita campos desconhecidos.
- Consultas mantêm o `company_id` autenticado.
- Build frontend passou.
- Compilação Python passou.
- Os quinze endpoints de design foram registrados.
- Nenhuma publicação ou alteração de Draft ocorre na criação de preview.

## Failed

- Não foi executado E2E visual em navegador real.
- Não foi validada uma Render Specification real vinda do provider: `EMERGENT_LLM_KEY` não está disponível.
- Não foi executado E2E com dois tenants e MongoDB real.

## Known Limitations

A criação de Preview depende de uma Render Specification já persistida. A aprovação formal e o Apply ao Draft serão tratados na Fase 2.9.

A ação do Landing Builder atualiza a prévia local com a especificação retornada, mas não mantém uma tela histórica completa de todas as Preview Sessions. O endpoint de listagem já está disponível para essa evolução.

O build mantém dois warnings preexistentes de dependências de `useEffect` em `Agenda.jsx` e `Clients.jsx`; eles não foram alterados nesta fase.

## Security Notes

Todas as consultas de Render Specification e Preview Session incluem `company_id` autenticado. `preview_id` não substitui o filtro de tenant. Nenhuma rota de preview altera publicação, Draft, usuários, memberships, pagamentos ou dados operacionais.

## Performance Notes

A listagem retorna no máximo vinte previews. A expiração é verificada sob demanda e usa índice por `expires_at`. O Render Specification é validado antes de entrar na sessão.

## Current Pause Point

A Fase 2.8 está pronta para checkpoint após testes locais e build. O avanço está pausado antes da Fase 2.9 até que provider, storage, MongoDB e fluxo visual sejam validados em ambiente configurado ou a limitação seja formalmente aceita.

## Next Phase

Fase 2.9 — Apply Design, somente após resolver ou aceitar formalmente os bloqueios das Fases 2.1 a 2.8.

## Git Commit

`6dcbab8` — `AI Digital Art Director — Phase 2.8 Preview Application`

## Timestamp

2026-09-17T22:33:00-03:00
