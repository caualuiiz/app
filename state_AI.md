# AI PROJECT STATE

## Current Phase

Fase 2.9 — Apply Design

## Status

IMPLEMENTED WITH LIMITATIONS

As Fases 2.1 a 2.9 possuem contratos e integrações incrementais. A sequência completa de Digital Art Director possui análise, direção, sistema de design, layout, especificação declarativa, renderer, preview e aplicação controlada ao Draft.

## Implemented

As Fases 2.1 a 2.8 permanecem implementadas com seus contratos, serviços, persistência, renderer AI_SPEC/LEGACY e Preview Sessions.

A Fase 2.9 adiciona `ApplyDesignRequest` com `preview_id`, `request_id` obrigatório para idempotência e `expected_draft_version` opcional para controle otimista de concorrência.

O serviço valida que o Preview pertence à empresa autenticada, está em estado `CREATED` ou `ACTIVE` e não expirou. A Render Specification é validada novamente antes de ser aplicada.

A aplicação grava a especificação em `landing_pages.draft_render_spec`, incrementa `landing_pages.draft_version` e atualiza `draft_updated_at`. O campo `state.is_published` não é alterado e não existe publicação automática.

Antes da aplicação, o serviço verifica a versão esperada. O update do Draft usa filtro de versão atual para impedir que duas aplicações concorrentes sobrescrevam a mesma versão. Conflitos retornam HTTP 409.

Cada aplicação cria um snapshot em `draft_versions`, contendo versão anterior, versão nova, Preview, request, usuário, especificação anterior e nova especificação. Também cria uma decisão auditável em `landing_decisions` com operação `APPLY_DESIGN`.

Repetições com o mesmo `company_id` e `request_id` retornam a decisão existente com `idempotent=true`. Requests diferentes contra um Draft alterado falham com conflito de versão.

O Preview é marcado como `APPLIED` após a aplicação. Estados expirados, cancelados ou já aplicados não podem ser aplicados novamente.

## Files Created

- `backend/ai/design_application.py`
- `backend/ai/design_application_service.py`
- `tests/test_design_application.py`

## Files Modified

- `backend/routes_design.py`
- `backend/db.py`
- `frontend/src/pages/LandingBuilder.jsx`
- `state_AI.md`

## Endpoint Added

- `POST /api/design/apply-preview`

O endpoint exige membership ativa e papel `OWNER` ou `MANAGER`. O tenant é obtido da membership autenticada e não é aceito no payload.

## Frontend Integration

O Landing Builder recebeu a ação explícita `Aplicar ao Draft`. Ela só fica habilitada após a criação de uma Preview Session. A ação atualiza a prévia local com a especificação aplicada e informa que o Draft foi alterado sem publicar. O botão `Publicar` permanece separado.

## Database Changes

- Campo `draft_render_spec` em `landing_pages`.
- Campo incremental `draft_version` em `landing_pages`.
- Campo `draft_updated_at` em `landing_pages`.
- Nova coleção lógica `draft_versions` para snapshots.
- Nova coleção lógica `landing_decisions` para auditoria.
- Índice único `landing_decisions(company_id, request_id)`.
- Índice único `draft_versions(company_id, version)`.
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

- 37 testes backend cumulativos passaram.
- 3 testes frontend passaram.
- Request de Apply exige Preview e request idempotente.
- Campos desconhecidos e versões negativas são rejeitados.
- Filtro de Draft preserva o `company_id` e a versão esperada.
- A resposta de Apply sempre declara `published=false`.
- Build frontend passou.
- Compilação Python passou.
- O endpoint `apply-preview` foi registrado.
- Nenhuma publicação automática foi adicionada.

## Failed

- Não foi executado E2E visual em navegador real.
- Não foi validado Apply contra MongoDB real ou transação distribuída.
- Não foi executado E2E com dois tenants concorrentes.
- Não foi validado um Render Specification real vindo do provider: `EMERGENT_LLM_KEY` não está disponível.

## Known Limitations

O Apply grava Draft, snapshots e decisão em operações sequenciais. O filtro otimista impede sobrescrita concorrente, mas uma transação MongoDB multi-documento deverá ser habilitada em ambiente de produção com replica set para atomicidade completa entre Draft, snapshot, decisão e status do Preview.

A reversão visual de snapshots ainda não possui endpoint próprio. Os snapshots e versões ficam disponíveis para a próxima evolução de histórico/rollback.

A publicação continua sendo uma ação separada do Apply. O endpoint de publicação legado não foi alterado nesta fase.

O build mantém dois warnings preexistentes de dependências de `useEffect` em `Agenda.jsx` e `Clients.jsx`; eles não foram alterados nesta fase.

## Security Notes

Todas as consultas incluem `company_id` autenticado. `preview_id` e `request_id` não substituem o filtro de tenant. O Apply valida status, expiração e Render Specification antes de gravar. Nenhum segredo, token, cookie ou campo de outra empresa entra no Draft. `is_published` não é alterado pelo Apply.

## Performance Notes

O Apply usa índices por tenant/request e tenant/version. A especificação é validada antes da gravação. A resposta retorna apenas a especificação aplicada e metadados da decisão.

## Current Pause Point

A implementação das Fases 2.1–2.9 está concluída em nível de contrato, backend, frontend e testes locais. O próximo passo recomendado é configurar provider/MongoDB real e executar E2E multi-tenant antes de qualquer evolução de rollback, transações ou publicação AI_SPEC.

## Next Phase

Nenhuma nova fase 2.x foi iniciada. A arquitetura está pausada após a Fase 2.9 para validação integrada.

## Git Commit

`9add32e` — `AI Digital Art Director — Phase 2.9 Apply Design`

## Timestamp

2026-09-17T22:38:00-03:00
