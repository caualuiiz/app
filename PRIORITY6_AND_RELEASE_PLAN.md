# Prioridade 6 e plano de release

## Estado atual

A sandbox atual não possui `mongod`, `mongosh`, Docker, `MONGO_URL` ou `MONGO_TEST_DB`. Portanto, a validação contra MongoDB real ainda não foi certificada.

Foi adicionado o teste executável:

```bash
cd backend
MONGO_URL='mongodb+srv://<user>:<password>@<cluster>/?retryWrites=true&w=majority' \
MONGO_TEST_DB='saas_priority6_<run-id>' \
python -m pytest -q tests/test_real_mongodb_two_tenants.py -o addopts='-n 0'
```

O teste usa apenas `MONGO_TEST_DB`, executa `ping`, cria o índice parcial único de slots, verifica que dois tenants podem usar o mesmo horário sem enxergar os dados um do outro e dispara duas escritas concorrentes no mesmo tenant/profissional/data/horário. O teste exige exatamente um vencedor e um conflito `DuplicateKeyError`, e remove somente o banco descartável ao terminar.

## Critérios de aprovação da Prioridade 6

- [ ] Conexão MongoDB real responde ao `ping`.
- [ ] Índices de produção são criados sem colisões existentes.
- [ ] Tenant A não lê documentos do tenant B.
- [ ] Tenant B não lê documentos do tenant A.
- [ ] O mesmo horário pode existir em tenants diferentes.
- [ ] Duas reservas concorrentes do mesmo slot no mesmo tenant produzem 1 sucesso e 1 conflito.
- [ ] Atualização concorrente de slot também retorna conflito, sem alterar o documento de outro tenant.
- [ ] O teste é executado em replica set/Atlas antes de considerar transações multi-documento certificadas.

## Plano posterior, em ordem

### 7. E2E completo no navegador

1. Subir API com MongoDB de teste e frontend com `REACT_APP_BACKEND_URL` apontando para a API.
2. Registrar dois usuários/tenants independentes.
3. Completar onboarding de cada tenant.
4. Criar serviços, disponibilidade e clientes em ambos.
5. Confirmar que cada usuário só lista e altera os próprios dados.
6. Executar booking público por slug para cada tenant.
7. Executar recuperação de senha em ambiente de teste.
8. Executar editor de landing, preview, Apply e publicação.
9. Testar refresh, logout, role gates, upload e navegação mobile.
10. Capturar evidências de cada fluxo e falhas de console/rede.

### 8. Integrações reais

Executar somente com credenciais de teste/sandbox:

- OpenAI: chamada mínima do fluxo de Landing Brain, timeout, erro e resposta inválida.
- Stripe: Checkout, webhook assinado, evento duplicado e limite de plano.
- WhatsApp: verificação webhook, assinatura, envio de template e falha do provider.
- Render: domínio customizado, verificação e remoção em serviço de teste.
- E-mail: envio do link de recuperação e confirmação de que o token nunca aparece em logs.

### 9. Smoke test de produção

1. Verificar `/api/health` com HTTP 200.
2. Verificar CORS e cookies `Secure`.
3. Registrar/login/logout/refresh.
4. Criar tenant, serviço, disponibilidade e booking.
5. Confirmar/rejeitar booking.
6. Verificar landing pública, domínio e upload.
7. Verificar Stripe, WhatsApp, e-mail e cron.
8. Observar logs, latência, erros 5xx e idempotência.
9. Executar rollback plan e confirmar que nenhum segredo apareceu em logs.

## Auditoria final de prontidão

Aprovar somente quando Prioridades 6–9 tiverem evidência datada e reproduzível. O resultado deve separar `PASS`, `BLOCKED BY CREDENTIALS/INFRASTRUCTURE`, `FAIL` e riscos residuais. Nenhum teste em memória ou smoke de rota estática substitui os testes reais acima.
