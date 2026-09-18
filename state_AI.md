# AI PROJECT STATE

## Current Phase

Fase 2.1 — Visual Intelligence

## Status

IMPLEMENTED WITH LIMITATIONS

A camada de contratos, seleção company-scoped, persistência e endpoints da Visual Intelligence foi implementada. A análise real via provider existente depende de `EMERGENT_LLM_KEY`, storage configurado e imagens persistidas; esses serviços não estão disponíveis nesta sessão.

## Implemented

- Contratos Pydantic estruturados com `extra="forbid"`.
- Solicitação de análise com limite de oito imagens.
- Seleção de imagens somente a partir da galeria da landing da empresa autenticada.
- Verificação adicional contra registros da coleção `files` com o mesmo `company_id` e `is_deleted=false`.
- Contexto da empresa limitado a nome, tipo de negócio e descrição.
- Provider existente encapsulado em serviço próprio da Fase 2.1.
- Parsing e validação estrita do JSON retornado pelo provider.
- Persistência em `visual_profiles`.
- `request_id`, provider, modelo, timestamp e caminhos analisados persistidos.
- Endpoint para criar análise visual.
- Endpoint para recuperar perfis visuais da empresa autenticada.
- Índice MongoDB por `company_id` e `created_at`.

## Files Created

- `backend/ai/__init__.py`
- `backend/ai/visual.py`
- `backend/ai/visual_intelligence.py`
- `backend/routes_design.py`
- `tests/test_visual_intelligence.py`

## Files Modified

- `backend/server.py`
- `backend/db.py`
- `state_AI.md`

Também já existiam alterações anteriores, fora da implementação desta fase, em `backend/routes_landing.py`, `backend/server.py` e `frontend/package.json`.

## Endpoints Added

- `POST /api/design/analyze-images`
- `GET /api/design/visual-profile`

Ambos exigem membership ativa e papel `OWNER` ou `MANAGER`. O `company_id` é obtido da membership no backend; não é aceito no payload.

## Database Changes

- Nova coleção lógica `visual_profiles`.
- Novo índice: `visual_profiles(company_id, created_at desc)`.
- Nenhuma migração destrutiva.
- Nenhuma alteração foi feita no MongoDB nesta sessão.

## Tests

- `python3 -m pytest -q tests/test_visual_intelligence.py`
- `python3 -m compileall -q backend tests`
- Importação da aplicação FastAPI com variáveis locais de teste.
- Verificação dos caminhos OpenAPI.
- `git diff --check`.

## Passed

- 3 testes unitários da Fase 2.1 passaram.
- Contrato rejeita campos desconhecidos.
- Imagem de outro tenant é descartada.
- Imagem deletada é rejeitada.
- Compilação Python passou.
- Os endpoints `/api/design/analyze-images` e `/api/design/visual-profile` foram registrados.
- Nenhum segredo foi adicionado ao código.

## Failed

- Não foi executada análise real com provider: `EMERGENT_LLM_KEY` não está disponível.
- Não foi executada persistência real contra MongoDB Atlas: `MONGO_URL` e credenciais do ambiente não estão disponíveis.
- Não foi executado E2E com dois tenants.

## Known Limitations

- A análise visual utiliza o provider existente `emergentintegrations` e o modelo `gpt-4o-mini`; a abstração geral `AIProvider`/`ClaudeProvider` será tratada em etapa posterior, sem avançar automaticamente nesta fase.
- Os campos numéricos e descritores dependem de JSON válido do provider.
- A inclusão de foto da empresa depende de a imagem possuir registro correspondente na coleção `files`.
- Não há frontend específico para os novos endpoints nesta fase.

## Security Notes

- Nenhum `company_id` é aceito no payload.
- A membership autenticada define o tenant.
- Imagens são selecionadas pela galeria da landing e confirmadas na coleção `files` do mesmo tenant.
- O contexto enviado ao provider não contém senha, token, cookie, segredo, API key ou dados de outro tenant.
- O JSON do provider é validado com schema fechado.
- Falhas do provider não expõem credenciais ao cliente.

## Performance Notes

- Máximo de oito imagens por análise.
- Máximo de vinte perfis retornados no endpoint de leitura.
- Índice por tenant e data de criação.
- Cada imagem é carregada uma vez e convertida em base64 somente durante a requisição.

## Current Pause Point

A Fase 2.1 está pronta para checkpoint após os testes locais. O avanço está pausado antes da Fase 2.2 até que a integração real com provider/storage/MongoDB seja validada ou explicitamente aceita como limitação de ambiente.

## Next Phase

Fase 2.2 — Reference Intelligence, somente após resolver ou aceitar formalmente os bloqueios da Fase 2.1.

## Git Commit

`45fe180` — `AI Digital Art Director — Phase 2.1 Visual Intelligence`

## Timestamp

2026-09-17T22:09:00-03:00
