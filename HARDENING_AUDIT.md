# Auditoria de hardening — prioridades reais

Data da execução: 2026-09-25/26

## Resumo executivo

As prioridades 1–5 foram implementadas e verificadas localmente. A prioridade 7 teve um smoke test de navegador contra as rotas públicas da SPA. As prioridades 6, 8 e 9 não podem ser certificadas nesta sandbox porque não há MongoDB executável, URL de produção nem credenciais completas das integrações.

## Status por prioridade

| Ordem | Prioridade | Status | Evidência / bloqueio |
|---:|---|---|---|
| 1 | Recuperação de senha | **CONCLUÍDO + TESTADO LOCALMENTE** | Foram criadas as telas `/forgot-password` e `/reset-password`; o token só é retornado fora de produção; o link é configurável por `PASSWORD_RESET_URL_BASE`; enumeração de contas continua evitada. |
| 2 | Lockfiles front/back | **CONCLUÍDO + TESTADO LOCALMENTE** | Criados `frontend/package-lock.json` e `backend/requirements.lock`; CI e Render foram alterados para `npm ci`/`pip install` determinísticos. |
| 3 | Cookies dev/prod | **CONCLUÍDO + TESTADO LOCALMENTE** | `Secure=false` apenas fora de `ENVIRONMENT=production`; produção mantém `HttpOnly`, `SameSite=Lax` e `Secure=true`. |
| 4 | Validação segura de upload | **CONCLUÍDO + TESTADO LOCALMENTE** | MIME declarado passou a ser conferido contra assinatura dos bytes para JPEG, PNG, GIF e WebP; extensão armazenada é canônica e gerada internamente. |
| 5 | Reset atômico | **CONCLUÍDO + TESTADO LOCALMENTE** | Token é reivindicado com `find_one_and_update` condicional (`used=false` e não expirado), evitando reutilização concorrente. |
| 6 | MongoDB real + dois tenants | **PENDENTE DE INFRAESTRUTURA EXTERNA** | Não há `mongod`, `mongosh`, Docker, `MONGO_URL` ou `DB_NAME` disponíveis. A suíte local existente continua em memória; não equivale a um teste contra MongoDB real. |
| 7 | E2E no navegador | **PARCIALMENTE TESTADO** | Chromium headless renderizou `/forgot-password` e `/reset-password?token=...` via servidor React com history fallback. O fluxo autenticado completo não foi executado porque não há backend/MongoDB configurados. |
| 8 | Integrações externas | **PENDENTE DE CREDENCIAIS** | Stripe, WhatsApp e Render estão sem credenciais; não foram feitas chamadas externas. A chave OpenAI presente no ambiente não foi usada para evitar chamadas não autorizadas/custos. |
| 9 | Smoke test em produção + prontidão | **PENDENTE DE PRODUÇÃO** | Não existe URL de produção fornecida nem ambiente implantado acessível. O runbook foi atualizado, mas health check, login, booking, Stripe, WhatsApp e domínio customizado ainda precisam ser validados após deploy. |

## Testes executados

- `python -m compileall -q backend tests`: **PASS**
- `python -m pytest -q tests backend/tests -o addopts='-n 0'`: **47 passed, 1 warning**
- `CI=true npm test -- --watchAll=false --runInBand`: **3 passed**
- `npm run build`: **PASS**
- `npm ci --legacy-peer-deps --ignore-scripts`: **PASS**
- `uv pip compile requirements.txt --output-file requirements.lock`: **PASS**
- Chromium headless em `/forgot-password`: **PASS**
- Chromium headless em `/reset-password`: **PASS**

## Riscos residuais

1. O endpoint de recuperação ainda precisa de um provedor transacional de e-mail para ser funcional em produção. O código não finge que o token foi enviado.
2. `npm install --package-lock-only` reportou **33 vulnerabilidades transitivas** no grafo atual: 12 baixas, 6 moderadas e 15 altas. O lockfile foi preservado; uma atualização orientada por compatibilidade ainda é necessária.
3. O reset atômico evita reutilização concorrente do token, mas a alteração do usuário e a revogação das sessões ainda não estão numa transação MongoDB multi-documento. Isso requer replica set/transação em produção.
4. A validação de upload usa assinaturas mínimas de arquivo; uma validação completa de decodificação e re-encoding de imagem seria mais forte contra arquivos poliglotas/corrompidos.
5. O smoke test do navegador validou a renderização das rotas, não o fluxo autenticado completo.

## Arquivos principais alterados

- `backend/routes_auth.py`
- `backend/models.py`
- `backend/auth.py`
- `backend/routes_uploads.py`
- `backend/.env.example`
- `backend/requirements.lock`
- `backend/tests/test_security_hardening.py`
- `frontend/src/App.js`
- `frontend/src/pages/Login.jsx`
- `frontend/src/pages/ForgotPassword.jsx`
- `frontend/src/pages/ResetPassword.jsx`
- `frontend/package-lock.json`
- `.github/workflows/ci.yml`
- `render.yaml`
- `PRODUCTION_RUNBOOK.md`
