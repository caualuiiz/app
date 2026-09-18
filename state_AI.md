# AI PROJECT STATE

## Current Phase

Fase 2.6 — Render Specification

## Status

IMPLEMENTED WITH LIMITATIONS

As Fases 2.1 a 2.6 possuem contratos fechados, contexto company-scoped, persistência e endpoints protegidos. A geração real via provider e a persistência real em MongoDB Atlas dependem de serviços externos não disponíveis nesta sessão.

## Implemented

A Fase 2.1 — Visual Intelligence — analisa imagens autorizadas da galeria e persiste perfis visuais.

A Fase 2.2 — Reference Intelligence — analisa referências para extrair princípios de design.

A Fase 2.3 — Art Direction — cria direção visual estruturada.

A Fase 2.4 — Design System — cria tokens estruturados e validáveis.

A Fase 2.5 — Layout Plan — define a composição da página por seções, layouts permitidos, conteúdo, interação, motion e responsive.

A Fase 2.6 adiciona uma Render Specification declarativa e fechada, que funciona como ponte entre a IA e o renderer. O contrato cobre `version`, `theme`, `typography`, `spacing`, `sections`, `motion`, `interactions`, `responsive`, `media` e `accessibility`.

Cada seção possui tipo permitido, modo de layout permitido, referências estruturadas, tipografia, espaçamento, cores, motion, interação, comportamento responsivo, acessibilidade e fallback. Referências só podem usar os namespaces `landing`, `company`, `media` ou `profile`.

A especificação não aceita HTML, CSS, JavaScript, React, Python, SQL, shell, comandos ou campos desconhecidos. O provider é instruído a retornar somente dados declarativos; a resposta é validada contra `RenderSpecification` antes da persistência.

As especificações são persistidas em `render_specifications` com `request_id`, empresa, usuário, Layout Plan de origem, provider, modelo e timestamp.

## Files Created

- `backend/ai/render_specification.py`
- `backend/ai/render_specification_service.py`
- `tests/test_render_specification.py`

## Files Modified

- `backend/routes_design.py`
- `backend/db.py`
- `state_AI.md`

## Endpoints Added

- `POST /api/design/generate-render-spec`
- `GET /api/design/render-spec`

Os endpoints exigem membership ativa e papel `OWNER` ou `MANAGER`. O tenant é obtido da membership autenticada e não é aceito no payload.

## Database Changes

- Nova coleção lógica `render_specifications`.
- Novo índice: `render_specifications(company_id, created_at desc)`.
- Nenhuma migração destrutiva.
- Nenhuma alteração foi feita no MongoDB nesta sessão.

## Tests

- `python3 -m pytest -q`
- `python3 -m compileall -q backend tests`
- Importação da aplicação FastAPI com variáveis locais de teste.
- Verificação dos caminhos OpenAPI.
- `git diff --check`.

## Passed

- 30 testes cumulativos das Fases 2.1 a 2.6 passaram.
- Estrutura declarativa válida é aceita.
- Campos desconhecidos e código arbitrário são rejeitados.
- Referências fora dos namespaces permitidos são rejeitadas.
- IDs de seção duplicados são rejeitados.
- O payload não aceita `company_id` arbitrário.
- O contexto exclui campos sensíveis da empresa.
- Consultas de Layout Plan mantêm o `company_id` autenticado.
- Compilação Python passou.
- Os doze endpoints de design foram registrados.
- Nenhum segredo foi adicionado ao código.

## Failed

- Não foi executada geração real com provider: `EMERGENT_LLM_KEY` não está disponível.
- Não foi executada persistência real contra MongoDB Atlas: `MONGO_URL` e credenciais do ambiente não estão disponíveis.
- Não foi executado E2E com dois tenants.

## Known Limitations

A geração depende de um Layout Plan já persistido; quando nenhum `layout_plan_request_id` é informado, o serviço utiliza o Layout Plan mais recente da empresa.

A Render Specification foi criada como contrato backend; a interpretação no frontend e o fallback efetivo `AI_SPEC`/`LEGACY` pertencem à Fase 2.7.

O provider existente ainda é usado diretamente; a abstração `AIProvider`/`ClaudeProvider` permanece pendente. As Fases 2.7 a 2.9 não foram iniciadas.

## Security Notes

Nenhum `company_id` é aceito no payload. O Layout Plan é consultado com o `company_id` da membership. O contexto permite somente nome, tipo de negócio, descrição e plano validado. Não são incluídos senha, token, cookie, segredo, API key ou dados operacionais. O JSON do provider é validado com schema fechado. Não há execução de código nem referências arbitrárias.

## Performance Notes

A leitura de Render Specifications retorna no máximo vinte registros. A coleção possui índice por tenant e data. A especificação limita seções e referências para manter o payload controlado.

## Current Pause Point

A Fase 2.6 está pronta para checkpoint após testes locais. O avanço está pausado antes da Fase 2.7 até que o provider, storage e MongoDB sejam validados em ambiente configurado ou a limitação seja formalmente aceita.

## Next Phase

Fase 2.7 — Renderer Integration, somente após resolver ou aceitar formalmente os bloqueios das Fases 2.1 a 2.6.

## Git Commit

`7a13c96` — `AI Digital Art Director — Phase 2.6 Render Specification`

## Timestamp

2026-09-17T22:25:00-03:00
