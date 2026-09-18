# AI PROJECT STATE

## Current Phase

Fase 2.3 — Art Direction

## Status

IMPLEMENTED WITH LIMITATIONS

As Fases 2.1, 2.2 e 2.3 possuem contratos fechados, contexto company-scoped, persistência e endpoints protegidos. A geração real via provider e a persistência real em MongoDB Atlas dependem de serviços externos não disponíveis nesta sessão.

## Implemented

A Fase 2.1 — Visual Intelligence — analisa imagens autorizadas da galeria e persiste perfis visuais.

A Fase 2.2 — Reference Intelligence — analisa URL, descrição e imagens autorizadas para extrair princípios de design, sem copiar identidade ou layout proprietário.

A Fase 2.3 adiciona contrato estruturado de Art Direction com personalidade de marca, conceito visual, direção de arte, imagem, tipografia, cor, composição, motion, interação, 3D, background e conversão. A proposta também registra confiança, avisos e dados ausentes.

O contexto da geração é construído somente com dados relevantes da empresa, estado editorial da landing e os perfis visuais/de referência da mesma empresa. Senhas, tokens, cookies, segredos, API keys e campos operacionais não entram no contexto.

As propostas são persistidas em `art_directions` com `request_id`, usuário, empresa, perfis de origem, provider, modelo e timestamp.

## Files Created

- `backend/ai/art_direction.py`
- `backend/ai/art_direction_service.py`
- `tests/test_art_direction.py`

## Files Modified

- `backend/routes_design.py`
- `backend/db.py`
- `state_AI.md`

## Endpoints Added

- `POST /api/design/generate-art-direction`
- `GET /api/design/art-direction`

Os endpoints exigem membership ativa e papel `OWNER` ou `MANAGER`. O tenant é obtido da membership autenticada e não é aceito no payload.

## Database Changes

- Nova coleção lógica `art_directions`.
- Novo índice: `art_directions(company_id, created_at desc)`.
- Nenhuma migração destrutiva.
- Nenhuma alteração foi feita no MongoDB nesta sessão.

## Tests

- `python3 -m pytest -q`
- `python3 -m compileall -q backend tests`
- Importação da aplicação FastAPI com variáveis locais de teste.
- Verificação dos caminhos OpenAPI.
- `git diff --check`.

## Passed

- 11 testes cumulativos das Fases 2.1, 2.2 e 2.3 passaram.
- Contrato de Art Direction rejeita campos desconhecidos.
- Requisição não aceita `company_id` arbitrário.
- Contexto exclui `password_hash`, API key e `is_published`.
- Query de perfis mantém o `company_id` autenticado.
- Compilação Python passou.
- Os seis endpoints de design foram registrados.
- Nenhum segredo foi adicionado ao código.

## Failed

- Não foi executada geração real com provider: `EMERGENT_LLM_KEY` não está disponível.
- Não foi executada persistência real contra MongoDB Atlas: `MONGO_URL` e credenciais do ambiente não estão disponíveis.
- Não foi executado E2E com dois tenants.

## Known Limitations

A proposta depende de perfis visuais e de referência já persistidos quando IDs são fornecidos; sem esses perfis, a geração ainda pode usar o contexto da empresa e da landing, mas não possui evidência visual adicional.

A abstração geral `AIProvider`/`ClaudeProvider` continua pendente. A implementação reutiliza o provider existente, conforme o plano incremental.

Não há frontend específico para os novos endpoints nesta fase. As Fases 2.4 a 2.9 não foram iniciadas.

## Security Notes

Nenhum `company_id` é aceito no payload. Perfis visuais e de referência são sempre consultados com `company_id` da membership. O contexto permite somente campos editoriais e públicos da empresa. O estado publicado não é enviado como decisão de Art Direction. O JSON do provider é validado com schema fechado. O prompt proíbe inventar fatos e copiar referências.

## Performance Notes

As consultas de perfis são limitadas ao tenant e retornam o registro solicitado ou o mais recente. A leitura de propostas retorna no máximo vinte registros. A coleção possui índice por tenant e data.

## Current Pause Point

A Fase 2.3 está pronta para checkpoint após testes locais. O avanço está pausado antes da Fase 2.4 até que o provider, storage e MongoDB sejam validados em ambiente configurado ou a limitação seja formalmente aceita.

## Next Phase

Fase 2.4 — Design System, somente após resolver ou aceitar formalmente os bloqueios das Fases 2.1 a 2.3.

## Git Commit

`aa63fa9` — `AI Digital Art Director — Phase 2.3 Art Direction`

## Timestamp

2026-09-17T22:16:00-03:00
