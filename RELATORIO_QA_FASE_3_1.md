# Relatório QA — Fase 3.1

**Data:** 2026-09-17/18  
**Repositório:** `caualuiiz/app`  
**Branch:** `main`  
**Escopo:** Quality Assurance e testes de integração End-to-End das Fases 2.1–2.9.

## Objetivo

A Fase 3.1 verifica se os contratos e fluxos implementados nas Fases 2.1 a 2.9 permanecem compatíveis entre si, com atenção especial ao isolamento multi-tenant, ao ciclo Render Specification → Preview → Apply, à idempotência, à expiração e à separação entre Draft e Published.

A validação foi executada localmente e não alterou funcionalidades de produção, banco real, frontend de produção ou publicação.

## Fluxos inventariados

| Fluxo | Verificação | Resultado |
|---|---|---|
| Visual Intelligence | Contratos, tenant e persistência cobertos pela suíte existente | PASS |
| Reference Intelligence | Contratos, fontes e isolamento cobertos pela suíte existente | PASS |
| Art Direction | Validação estruturada e tenant cobertos pela suíte existente | PASS |
| Design System | Tokens fechados e isolamento cobertos pela suíte existente | PASS |
| Layout Plan | Composição, IDs e modos permitidos cobertos pela suíte existente | PASS |
| Render Specification | Schema fechado e referências seguras cobertos pela suíte existente | PASS |
| Renderer Integration | AI_SPEC/LEGACY, whitelist e referências públicas cobertos pelos testes frontend | PASS |
| Preview Application | Criação, expiração e tenant cobertos pela suíte existente | PASS |
| Apply Design | Preview → Draft, snapshot, decisão, idempotência e concorrência cobertos pela suíte integrada | PASS |

## Teste integrado principal

O teste `tests/test_phase31_integration.py` simula bancos company-scoped em memória e executa o fluxo completo:

1. obtém uma Render Specification da empresa;
2. cria uma Preview Session;
3. aplica o Preview ao Draft;
4. confirma incremento de `draft_version`;
5. confirma criação de snapshot em `draft_versions`;
6. confirma criação de decisão em `landing_decisions`;
7. confirma que `state.is_published` continua `false`;
8. confirma que o Preview muda para `APPLIED`;
9. confirma que outro tenant recebe `404`;
10. repete o mesmo request e confirma `idempotent=true`;
11. tenta aplicar versão obsoleta e confirma `409`;
12. tenta aplicar Preview expirado e confirma `409`.

## Resultados

### Backend

```text
python3 -m pytest -q
40 passed, 1 warning
```

```text
python3 -m compileall -q backend tests
PASS
```

```text
git diff --check
PASS
```

A suíte inclui os testes unitários das Fases 2.1–2.9 e três testes integrados novos da Fase 3.1.

### Frontend

```text
CI=true npm test -- --watchAll=false --runInBand
3 passed
```

```text
npm run build
PASS
```

O build mantém dois warnings preexistentes de dependências de `useEffect` em `frontend/src/pages/Agenda.jsx` e `frontend/src/pages/Clients.jsx`. Nenhum desses arquivos foi alterado pela Fase 3.1.

## Controles de segurança verificados

Os testes confirmam que consultas de Preview e Apply incluem o tenant autenticado. `preview_id` e `request_id` não substituem o filtro de `company_id`. O Apply rejeita Preview expirado ou já aplicado, não aceita versão negativa e não aceita `company_id` no payload.

O Apply grava somente campos de Draft, snapshots e decisões. `state.is_published` não é alterado. A publicação permanece uma ação separada.

Os testes QA não executam comandos, não apagam dados, não usam banco real e não expõem segredos. O teste frontend do renderer mantém a rejeição de campos desconhecidos, referências inseguras e IDs duplicados.

## Bloqueios e limitações

Não foi executado E2E em navegador real. Não foi executado contra MongoDB Atlas, provider de IA ou dois processos concorrentes reais. O teste de concorrência é determinístico e verifica o filtro otimista de versão, mas não substitui um teste distribuído com replica set.

A atomicidade completa entre atualização do Draft, snapshot, decisão e status do Preview requer transação MongoDB multi-documento em ambiente com replica set. Esse requisito permanece documentado na Fase 2.9.

O primeiro comando da Fase 3.1 revelou que `pytest-asyncio` não está instalado. O harness foi corrigido para usar `asyncio.run` da biblioteca padrão, sem alterar dependências ou produção.

## Recomendações

Antes de publicar AI_SPEC em produção, configurar provider e MongoDB real, executar E2E com dois tenants, validar transações multi-documento, testar expiração com relógio controlado e realizar inspeção visual em navegador. Em seguida, adicionar cobertura de rollback de snapshots e de falhas parciais entre as coleções.

## Conclusão

A Fase 3.1 passou em nível local: os contratos das Fases 2.1–2.9 são compatíveis na suíte integrada, o ciclo Preview → Apply mantém o isolamento de tenant, a idempotência e o controle de versão, e a publicação permanece separada. Os bloqueios restantes são de ambiente integrado e validação operacional, não falhas observadas na suíte local.
