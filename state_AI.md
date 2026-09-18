# AI PROJECT STATE

## Current Phase

Fase 2.7 — Renderer Integration

## Status

IMPLEMENTED WITH LIMITATIONS

As Fases 2.1 a 2.7 possuem contratos e integrações incrementais. A Render Specification pode ser validada no frontend e interpretada por um renderer declarativo seguro, com fallback para o renderer legado. A geração real via provider e a persistência real em MongoDB Atlas dependem de serviços externos não disponíveis nesta sessão.

## Implemented

As Fases 2.1 a 2.6 permanecem implementadas com seus contratos, serviços, persistência e endpoints.

A Fase 2.7 adiciona `isSafeRenderSpec`, que valida a versão, campos fechados, cores hexadecimais, tipos de seção, modos de layout, IDs únicos, referências estruturadas e namespaces permitidos.

Foi criado `AISpecRenderer`, que interpreta somente estruturas previamente definidas. Ele não executa HTML, CSS, JavaScript, React, comandos ou código retornado pela IA. O renderer usa componentes React fixos, classes de layout pré-definidas e resolução limitada de referências públicas.

`LandingPreview` agora aceita uma Render Specification opcional. Quando ela passa a validação, renderiza com `AI_SPEC`; quando está ausente ou inválida, usa automaticamente o renderer `LEGACY` existente. `LandingPreview`, `PublicLanding` e `VisualEditor` foram preservados.

O Landing Builder carrega a especificação autenticada mais recente de forma opcional. Se a chamada falhar ou não houver especificação, o preview continua funcionando com LEGACY. A landing pública aceita uma especificação somente se o backend futuramente a fornecer no campo aprovado; como não há aprovação/publicação de AI_SPEC nesta fase, o comportamento público atual permanece LEGACY.

As referências do frontend são resolvidas apenas para campos públicos permitidos da empresa, caminhos editoriais permitidos da landing e imagens da galeria. Propriedades sensíveis não são resolvidas.

## Files Created

- `frontend/src/lib/renderSpec.js`
- `frontend/src/lib/renderSpec.test.js`
- `frontend/src/components/AISpecRenderer.jsx`

## Files Modified

- `frontend/src/components/LandingPreview.jsx`
- `frontend/src/pages/LandingBuilder.jsx`
- `frontend/src/pages/PublicLanding.jsx`
- `state_AI.md`

## Endpoints Added

Nenhum endpoint novo foi necessário nesta fase. O frontend reutiliza `GET /api/design/render-spec` criado na Fase 2.6.

## Database Changes

Nenhuma alteração de banco nesta fase.

## Tests

- `CI=true npm test -- --watchAll=false --runInBand`
- `npm run build`
- `python3 -m pytest -q`
- `python3 -m compileall -q backend tests`
- `git diff --check`.

## Passed

- 3 testes frontend do validador AI_SPEC passaram.
- O validador rejeita campos extras, referências inseguras e IDs duplicados.
- O resolver rejeita propriedades sensíveis e só permite campos públicos.
- 30 testes backend cumulativos passaram.
- Build frontend passou.
- Compilação Python passou.
- Nenhuma ocorrência de `dangerouslySetInnerHTML`, `innerHTML`, `eval`, `new Function` ou execução de comandos foi adicionada.

## Failed

- Não foi executado E2E visual em navegador real.
- Não foi validado um Render Specification real vindo do provider: `EMERGENT_LLM_KEY` não está disponível.
- Não foi executado E2E com dois tenants.

## Known Limitations

O renderer AI_SPEC cobre os tipos estruturados previstos, mas não tenta reproduzir todos os detalhes visuais possíveis de uma especificação futura. Motion e interação são interpretados como dados declarativos e não executam comportamento arbitrário nesta fase.

O endpoint público não expõe automaticamente Render Specifications não aprovadas. O fluxo de Preview/Apply e a separação formal Draft/Preview/Published serão tratados nas Fases 2.8 e 2.9.

O build mantém dois warnings preexistentes de dependências de `useEffect` em `frontend/src/pages/Agenda.jsx` e `frontend/src/pages/Clients.jsx`; eles não foram alterados nesta fase.

## Security Notes

A whitelist de campos existe no nível superior e nas seções. Referências só aceitam namespaces estruturados. O resolver público de empresa usa uma lista explícita de campos permitidos e não retorna senhas, tokens, cookies, segredos ou API keys. Nenhum código da IA é executado ou injetado no DOM.

## Performance Notes

Imagens do AI_SPEC usam `loading="lazy"`. O renderer usa componentes fixos e classes conhecidas. Falha de validação não bloqueia o preview: o fallback LEGACY é determinístico.

## Current Pause Point

A Fase 2.7 está pronta para checkpoint após testes locais e build. O avanço está pausado antes da Fase 2.8 até que o provider, storage, MongoDB e fluxo visual sejam validados em ambiente configurado ou a limitação seja formalmente aceita.

## Next Phase

Fase 2.8 — Preview Application, somente após resolver ou aceitar formalmente os bloqueios das Fases 2.1 a 2.7.

## Git Commit

`05f40a0` — `AI Digital Art Director — Phase 2.7 Renderer Integration`

## Timestamp

2026-09-17T22:29:00-03:00
