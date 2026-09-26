# Contributing

## Issue first
Toda mudança relevante começa por uma Issue com objetivo, escopo, critérios de aceitação, riscos/dependências e estratégia de testes. Correções triviais de documentação ou typo podem ser feitas diretamente, mas a exceção deve ser evidente no PR.

## Pull requests
- Vincule a PR à Issue correspondente; use `Closes #<number>` quando a PR concluir a Issue.
- Preencha o template integralmente.
- Não faça push direto em `main` quando a mudança for relevante.
- Aguarde CI verde e os reviews obrigatórios antes do merge.

## Architecture Review
Mudanças que afetam autenticação, multi-tenancy, concorrência, MongoDB, contratos de API, integrações externas, observabilidade, segurança ou performance devem incluir o checklist de [`docs/ARCHITECTURE_REVIEW_CHECKLIST.md`](docs/ARCHITECTURE_REVIEW_CHECKLIST.md).

## Quality gates
Execute antes de abrir a PR:

```bash
python -m compileall -q backend tests
python -m pytest -q tests backend/tests -o addopts='-n 0'
cd frontend && CI=true npm test -- --watchAll=false --runInBand && npm run build
cd .. && git diff --check
```

Testes que dependem de MongoDB, credenciais ou serviços externos devem ser marcados/documentados como condicionais. Nunca declare um teste não executado como aprovado.

## Definition of Done
Use [`docs/DEFINITION_OF_DONE.md`](docs/DEFINITION_OF_DONE.md). Segurança, isolamento entre tenants, riscos residuais e rollback devem ser registrados quando aplicável.
