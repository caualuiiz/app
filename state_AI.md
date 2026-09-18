# AI PROJECT STATE

## Current Phase

Fase 3.2 — Claude Provider + AI Provider Factory + Orchestrator

## Status

IMPLEMENTADA NO BRANCH `feature/ai-phase-3.2`

A arquitetura de provider de IA foi adicionada sobre o pipeline das Fases 2.1–2.9 e o QA da Fase 3.1, sem alterar o isolamento multi-tenant existente.

## Implementado

- Interface abstrata `AIProvider`.
- `ClaudeProvider` com integração assíncrona ao SDK Anthropic.
- `ProviderFactory` com seleção por `AI_PROVIDER`.
- `AIOrchestrator` com contexto seguro e sanitização de identificadores/segredos.
- Contrato Pydantic `StructuredDecision`.
- Validador de decisão com bloqueio de campos sensíveis.
- Serviço `create_ai_decision` com leitura tenant-scoped dos artefatos de IA existentes.
- Endpoint autenticado `POST /api/design/ai-decision` para OWNER/MANAGER.
- Persistência em `landing_decisions`.
- Dependência `anthropic` adicionada ao backend.
- Testes unitários para sanitização, validação e configuração do Claude.

## Segurança

- `company_id` e `user_id` continuam vindo exclusivamente da associação autenticada.
- O contexto enviado ao provider remove identificadores de tenant e campos sensíveis.
- A decisão retornada pelo provider passa por validação Pydantic antes de ser persistida.
- Nenhuma chave Anthropic foi adicionada ao repositório.
- O endpoint não expõe `company_id` ou `user_id` na resposta.

## Limitações

- A chamada real à Anthropic ainda depende de `ANTHROPIC_API_KEY` e `ANTHROPIC_MODEL` configurados no ambiente de execução.
- O modelo default legado do adapter é provisório; a Fase 3.3 deve exigir e validar a configuração real do modelo.
- Não foi executado aqui um E2E real contra Anthropic/MongoDB de produção.
- A execução de testes no ambiente remoto do GitHub ainda precisa ser confirmada por CI ou ambiente local configurado.

## Current Pause Point

A implementação de código da Fase 3.2 está no branch `feature/ai-phase-3.2`. O próximo passo é a Fase 3.3: configuração segura das variáveis Anthropic/MongoDB, primeiro teste real do provider e validação do fluxo completo com persistência.

## Commits

- `3275de9` — criação da interface `AIProvider`.
- Commits subsequentes no branch adicionam contrato, validator, factory, ClaudeProvider, orchestrator, service, endpoint, dependência e testes.

## Timestamp

2026-09-18
