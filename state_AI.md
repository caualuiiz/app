# AI PROJECT STATE

## Current Phase

Fase 2.2 — Reference Intelligence

## Status

IMPLEMENTED WITH LIMITATIONS

As Fases 2.1 e 2.2 possuem contratos fechados, escopo por empresa, persistência e endpoints protegidos. A análise real via provider e a persistência real em MongoDB Atlas continuam dependentes de variáveis e serviços externos não disponíveis nesta sessão.

## Implemented

A Fase 2.1 — Visual Intelligence — permanece implementada com contratos, análise de imagens da galeria, persistência em `visual_profiles` e endpoints de perfil visual.

A Fase 2.2 adiciona contratos Pydantic fechados para URLs, descrições e imagens de referência. A requisição exige pelo menos uma fonte e aceita somente campos conhecidos. As imagens são resolvidas exclusivamente pela galeria da landing da empresa autenticada e confirmadas na coleção `files` pelo mesmo `company_id`.

O serviço de Reference Intelligence envia ao provider apenas a URL fornecida, a descrição, imagens autorizadas e um contexto mínimo da empresa. O prompt instrui a extrair princípios de design, sem copiar textos, logos, identidade, imagens, código ou layout proprietário. A resposta é validada contra `ReferenceAnalysis` antes da persistência.

Os resultados são persistidos em `reference_profiles`, com `request_id`, empresa, usuário, fontes, caminhos das imagens, provider, modelo e timestamp. Foi criado índice por empresa e data.

## Files Created

- `backend/ai/reference.py`
- `backend/ai/reference_intelligence.py`
- `tests/test_reference_intelligence.py`

## Files Modified

- `backend/routes_design.py`
- `backend/db.py`
- `state_AI.md`

## Endpoints Added

- `POST /api/design/analyze-references`
- `GET /api/design/reference-profile`

Os endpoints exigem membership ativa e papel `OWNER` ou `MANAGER`. O tenant é obtido da membership autenticada; não existe `company_id` no payload.

## Database Changes

- Nova coleção lógica `reference_profiles`.
- Novo índice: `reference_profiles(company_id, created_at desc)`.
- Nenhuma migração destrutiva.
- Nenhuma alteração foi feita no MongoDB nesta sessão.

## Tests

- `python3 -m pytest -q`
- `python3 -m compileall -q backend tests`
- Importação da aplicação FastAPI com variáveis locais de teste.
- Verificação dos caminhos OpenAPI.
- `git diff --check`.

## Passed

- 7 testes unitários das Fases 2.1 e 2.2 passaram.
- Requisição sem URL, descrição ou imagem é rejeitada.
- Contrato rejeita campos desconhecidos.
- Imagem de outro tenant é descartada.
- Imagem sem registro autorizado é rejeitada.
- Compilação Python passou.
- Os quatro endpoints de design foram registrados.
- Nenhum segredo foi adicionado ao código.

## Failed

- Não foi executada análise real com provider: `EMERGENT_LLM_KEY` não está disponível.
- Não foi executada persistência real contra MongoDB Atlas: `MONGO_URL` e credenciais do ambiente não estão disponíveis.
- Não foi executado E2E com dois tenants.

## Known Limitations

A análise de URL é entregue ao provider como fonte textual; não há crawler ou captura automática de screenshot nesta fase. A análise de imagens usa somente imagens já presentes na galeria da landing e autorizadas no storage.

A abstração geral `AIProvider`/`ClaudeProvider` continua pendente para fase posterior. A implementação reutiliza o provider existente, conforme o plano incremental.

Não há frontend específico para os novos endpoints nesta fase. As Fases 2.3 a 2.9 não foram iniciadas.

## Security Notes

Nenhum `company_id` é aceito no payload. A membership autenticada define o tenant. Imagens são selecionadas pela galeria da landing e confirmadas na coleção `files` do mesmo tenant. O contexto não contém senha, token, cookie, segredo ou API key. O JSON do provider é validado com schema fechado. O prompt instrui a extrair princípios e proíbe cópia de identidade ou layout proprietário.

## Performance Notes

Cada requisição aceita no máximo oito imagens. A leitura retorna no máximo vinte perfis. As consultas possuem índices por tenant e data. As imagens são carregadas somente quando selecionadas.

## Current Pause Point

A Fase 2.2 está pronta para checkpoint após testes locais. O avanço está pausado antes da Fase 2.3 até que o provider, storage e MongoDB sejam validados em ambiente configurado ou a limitação seja formalmente aceita.

## Next Phase

Fase 2.3 — Art Direction, somente após resolver ou aceitar formalmente os bloqueios das Fases 2.1 e 2.2.

## Git Commit

`30a992a` — `AI Digital Art Director — Phase 2.2 Reference Intelligence`

## Timestamp

2026-09-17T22:11:00-03:00
