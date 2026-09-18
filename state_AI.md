# AI PROJECT STATE

## Current Phase

Fase 2.4 — Design System

## Status

IMPLEMENTED WITH LIMITATIONS

As Fases 2.1, 2.2, 2.3 e 2.4 possuem contratos fechados, contexto company-scoped, persistência e endpoints protegidos. A geração real via provider e a persistência real em MongoDB Atlas dependem de serviços externos não disponíveis nesta sessão.

## Implemented

A Fase 2.1 — Visual Intelligence — analisa imagens autorizadas da galeria e persiste perfis visuais.

A Fase 2.2 — Reference Intelligence — analisa URL, descrição e imagens autorizadas para extrair princípios de design, sem copiar identidade ou layout proprietário.

A Fase 2.3 — Art Direction — cria uma direção visual estruturada com base nos dados da empresa e nos perfis anteriores.

A Fase 2.4 adiciona um Design System estruturado e validável, derivado da Art Direction. O contrato cobre colors, typography, spacing, radius, grid, motion, visual, responsive, notas de acessibilidade, confiança e avisos.

As cores exigem formato hexadecimal de seis dígitos. O motion aceita somente `LOW`, `MEDIUM` ou `HIGH`. Os tokens de espaçamento, radius, tipografia, grid, visual e responsive possuem schemas fechados e limites de tamanho.

O contexto enviado ao provider inclui somente dados públicos mínimos da empresa e a Art Direction validada. A resposta é validada contra `DesignSystem` antes da persistência.

Os resultados são persistidos em `design_systems` com `request_id`, empresa, usuário, Art Direction de origem, provider, modelo e timestamp.

## Files Created

- `backend/ai/design_system.py`
- `backend/ai/design_system_service.py`
- `tests/test_design_system.py`

## Files Modified

- `backend/routes_design.py`
- `backend/db.py`
- `state_AI.md`

## Endpoints Added

- `POST /api/design/generate-design-system`
- `GET /api/design/design-system`

Os endpoints exigem membership ativa e papel `OWNER` ou `MANAGER`. O tenant é obtido da membership autenticada e não é aceito no payload.

## Database Changes

- Nova coleção lógica `design_systems`.
- Novo índice: `design_systems(company_id, created_at desc)`.
- Nenhuma migração destrutiva.
- Nenhuma alteração foi feita no MongoDB nesta sessão.

## Tests

- `python3 -m pytest -q`
- `python3 -m compileall -q backend tests`
- Importação da aplicação FastAPI com variáveis locais de teste.
- Verificação dos caminhos OpenAPI.
- `git diff --check`.

## Passed

- 17 testes cumulativos das Fases 2.1 a 2.4 passaram.
- Tokens válidos são aceitos.
- Cores fora do formato hexadecimal são rejeitadas.
- Campos desconhecidos são rejeitados.
- O payload não aceita `company_id` arbitrário.
- O contexto exclui `password_hash` e API key.
- Consultas de Art Direction mantêm o `company_id` autenticado.
- Compilação Python passou.
- Os oito endpoints de design foram registrados.
- Nenhum segredo foi adicionado ao código.

## Failed

- Não foi executada geração real com provider: `EMERGENT_LLM_KEY` não está disponível.
- Não foi executada persistência real contra MongoDB Atlas: `MONGO_URL` e credenciais do ambiente não estão disponíveis.
- Não foi executado E2E com dois tenants.

## Known Limitations

A geração depende de uma Art Direction já persistida; quando nenhum `art_direction_request_id` é informado, o serviço utiliza a Art Direction mais recente da empresa. O provider existente ainda é usado diretamente; a abstração `AIProvider`/`ClaudeProvider` permanece pendente para etapa posterior.

Não há frontend específico para os novos endpoints nesta fase. As Fases 2.5 a 2.9 não foram iniciadas.

## Security Notes

Nenhum `company_id` é aceito no payload. A Art Direction é sempre consultada com o `company_id` da membership. O contexto permite somente nome, tipo de negócio, descrição e direção de arte validada. Não são incluídos senha, token, cookie, segredo, API key ou dados operacionais. O JSON do provider é validado com schema fechado e não pode conter código executável.

## Performance Notes

A leitura de Design Systems retorna no máximo vinte registros. A coleção possui índice por tenant e data. O contexto contém apenas tokens e dados editoriais necessários.

## Current Pause Point

A Fase 2.4 está pronta para checkpoint após testes locais. O avanço está pausado antes da Fase 2.5 até que o provider, storage e MongoDB sejam validados em ambiente configurado ou a limitação seja formalmente aceita.

## Next Phase

Fase 2.5 — Layout Plan, somente após resolver ou aceitar formalmente os bloqueios das Fases 2.1 a 2.4.

## Git Commit

`cb41a9e` — `AI Digital Art Director — Phase 2.4 Design System`

## Timestamp

2026-09-17T22:19:00-03:00
