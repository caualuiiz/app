# Architecture Review Checklist

Use este checklist em mudanças relevantes antes do merge.

## Contexto
- [ ] Issue vinculada e escopo claramente delimitado.
- [ ] Critérios de aceitação e estratégia de testes definidos.
- [ ] Dependências externas, migrações e rollback identificados.

## Segurança e tenancy
- [ ] Toda consulta e mutação é escopada pelo tenant autenticado.
- [ ] Não há confiança em `tenant_id` fornecido pelo cliente sem autorização server-side.
- [ ] Autenticação, autorização, cookies, tokens e logs foram revisados.
- [ ] Uploads, dados pessoais e segredos foram considerados.

## Consistência e concorrência
- [ ] Race conditions e idempotência foram analisadas.
- [ ] Índices/constraints/transações necessários estão definidos.
- [ ] Falhas parciais e retries não corrompem dados.

## API e MongoDB
- [ ] Contratos, status HTTP, validação e compatibilidade foram revisados.
- [ ] Índices, cardinalidade, TTL, migração e impacto de performance foram avaliados.
- [ ] Teste real de MongoDB é executado quando o escopo exigir.

## Integrações e operação
- [ ] Timeouts, retries, assinaturas/webhooks e idempotência foram avaliados.
- [ ] Observabilidade, métricas, logs sem segredos e alertas estão definidos.
- [ ] Rollback é executável e não exige alteração destrutiva de dados.
- [ ] Impacto de performance e custo foi considerado.

## Resultado
- [ ] Aprovado
- [ ] Aprovado com riscos registrados
- [ ] Bloqueado: descrever o bloqueio

Revisor(es):
Data:
Riscos residuais:
Plano de rollback:
