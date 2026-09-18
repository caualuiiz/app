# AI PROJECT STATE

## Current Phase

Fase 2.5 — Layout Plan

## Status

IMPLEMENTED WITH LIMITATIONS

As Fases 2.1 a 2.5 possuem contratos fechados, contexto company-scoped, persistência e endpoints protegidos. A geração real via provider e a persistência real em MongoDB Atlas dependem de serviços externos não disponíveis nesta sessão.

## Implemented

A Fase 2.1 — Visual Intelligence — analisa imagens autorizadas da galeria e persiste perfis visuais.

A Fase 2.2 — Reference Intelligence — analisa URL, descrição e imagens autorizadas para extrair princípios de design.

A Fase 2.3 — Art Direction — cria uma direção visual estruturada específica para o negócio.

A Fase 2.4 — Design System — cria tokens estruturados e validáveis para cores, tipografia, spacing, radius, grid, motion, visual e responsive.

A Fase 2.5 adiciona um Layout Plan estruturado e derivado do Design System. Cada seção possui `id`, propósito, modo de layout, fonte de conteúdo, tratamento visual, interação, motion e comportamento responsive. Os IDs de seção são únicos e os modos permitidos são uma enumeração fechada de experiências suportadas.

O contrato também inclui ritmo da página, estratégia responsive, acessibilidade, performance, confiança e avisos. A geração não força um padrão repetitivo de cards e não permite layout arbitrário.

O contexto enviado ao provider inclui somente dados públicos mínimos da empresa e o Design System validado da mesma empresa. A resposta é validada contra `LayoutPlan` antes da persistência.

Os planos são persistidos em `layout_plans` com `request_id`, empresa, usuário, Design System de origem, provider, modelo e timestamp.

## Files Created

- `backend/ai/layout_plan.py`
- `backend/ai/layout_plan_service.py`
- `tests/test_layout_plan.py`

## Files Modified

- `backend/routes_design.py`
- `backend/db.py`
- `state_AI.md`

## Endpoints Added

- `POST /api/design/generate-layout-plan`
- `GET /api/design/layout-plan`

Os endpoints exigem membership ativa e papel `OWNER` ou `MANAGER`. O tenant é obtido da membership autenticada e não é aceito no payload.

## Database Changes

- Nova coleção lógica `layout_plans`.
- Novo índice: `layout_plans(company_id, created_at desc)`.
- Nenhuma migração destrutiva.
- Nenhuma alteração foi feita no MongoDB nesta sessão.

## Tests

- `python3 -m pytest -q`
- `python3 -m compileall -q backend tests`
- Importação da aplicação FastAPI com variáveis locais de teste.
- Verificação dos caminhos OpenAPI.
- `git diff --check`.

## Passed

- 23 testes cumulativos das Fases 2.1 a 2.5 passaram.
- Layouts válidos são aceitos.
- IDs de seção duplicados são rejeitados.
- Modos de layout não permitidos são rejeitados.
- O payload não aceita `company_id` arbitrário.
- O contexto exclui campos sensíveis da empresa.
- Consultas de Design System mantêm o `company_id` autenticado.
- Compilação Python passou.
- Os dez endpoints de design foram registrados.
- Nenhum segredo foi adicionado ao código.

## Failed

- Não foi executada geração real com provider: `EMERGENT_LLM_KEY` não está disponível.
- Não foi executada persistência real contra MongoDB Atlas: `MONGO_URL` e credenciais do ambiente não estão disponíveis.
- Não foi executado E2E com dois tenants.

## Known Limitations

A geração depende de um Design System já persistido; quando nenhum `design_system_request_id` é informado, o serviço utiliza o Design System mais recente da empresa.

O provider existente ainda é usado diretamente; a abstração `AIProvider`/`ClaudeProvider` permanece pendente para etapa posterior. Não há frontend específico para os novos endpoints nesta fase.

As Fases 2.6 a 2.9 não foram iniciadas.

## Security Notes

Nenhum `company_id` é aceito no payload. O Design System é sempre consultado com o `company_id` da membership. O contexto permite somente nome, tipo de negócio, descrição e tokens validados. Não são incluídos senha, token, cookie, segredo, API key ou dados operacionais. O JSON do provider é validado com schema fechado e os modos de layout são enumerados.

## Performance Notes

A leitura de Layout Plans retorna no máximo vinte registros. A coleção possui índice por tenant e data. O contexto contém somente dados editoriais e tokens necessários.

## Current Pause Point

A Fase 2.5 está pronta para checkpoint após testes locais. O avanço está pausado antes da Fase 2.6 até que o provider, storage e MongoDB sejam validados em ambiente configurado ou a limitação seja formalmente aceita.

## Next Phase

Fase 2.6 — Render Specification, somente após resolver ou aceitar formalmente os bloqueios das Fases 2.1 a 2.5.

## Git Commit

`f6f74c0` — `AI Digital Art Director — Phase 2.5 Layout Plan`

## Timestamp

2026-09-17T22:22:00-03:00
