# AI PROJECT STATE

## Current Phase

Fase 3.3 — Configuração segura do Claude + MongoDB + primeiro teste real

## Status

IMPLEMENTAÇÃO E HARDENING CONCLUÍDOS; TESTE REAL BLOQUEADO SOMENTE POR CONFIGURAÇÃO/REDE DO AMBIENTE

A Fase 3.2 foi consolidada na branch `feature/ai-phase-3.2`. A Fase 3.3 endureceu a configuração do provider Claude, atualizou o adapter para Structured Outputs nativo e deixou um smoke test completo para MongoDB + Claude.

## Implementado

- Configuração centralizada de `AI_PROVIDER`, `ANTHROPIC_API_KEY` e `ANTHROPIC_MODEL`.
- Falha explícita para chave ausente, modelo ausente ou placeholder.
- `.env.example` criado em `backend/.env.example`.
- Regras do `.gitignore` atualizadas para impedir commit de arquivos de ambiente.
- SDK Anthropic atualizado para `anthropic>=1.0.0`.
- Adapter Claude migrado para `client.messages.parse()` com `StructuredDecision` Pydantic.
- Removido `temperature`, evitando incompatibilidade com modelos Claude atuais.
- Modelo de exemplo atualizado para `claude-sonnet-5`.
- Smoke test `backend/scripts/verify_phase33.py` criado para:
  1. validar variáveis necessárias;
  2. testar `MongoDB ping`;
  3. fazer uma chamada real ao Claude;
  4. validar e imprimir apenas o resultado seguro da decisão.
- Testes de configuração e provider ampliados.

## Validação local

- `python -m compileall`: PASS.
- Testes direcionados Fase 3.2/3.3: **6 passed**.
- O caminho do Structured Output nativo foi testado com mock do cliente Anthropic.
- Não houve exposição de segredo real.

## Segurança

- Nenhuma chave Anthropic foi adicionada ao GitHub.
- `company_id` e `user_id` continuam fora do contexto enviado ao provider.
- O resultado do provider continua passando por `StructuredDecision` e pelo validator antes da persistência.
- O smoke test não grava a resposta no MongoDB.
- O endpoint autenticado de decisão permanece restrito a OWNER/MANAGER.

## Verificação externa da integração

A documentação atual da Anthropic confirma Structured Outputs por `output_config.format` e o helper Python `messages.parse()`. Também confirma que o modelo legado usado anteriormente no adapter está aposentado; `claude-sonnet-5` está listado como ativo.

## Limitação atual

O primeiro teste real contra Anthropic e MongoDB ainda não foi executado neste ambiente porque não há `ANTHROPIC_API_KEY`/configuração MongoDB disponíveis aqui e o ambiente de execução não possui acesso externo para instalar o SDK.

O código para o teste real já está salvo em `backend/scripts/verify_phase33.py` e depende apenas das variáveis do `backend/.env.example`.

## Current Pause Point

A Fase 3.3 está tecnicamente preparada e validada localmente. O único item pendente é a execução do smoke test com credenciais reais e MongoDB acessível.

Depois desse teste real, o próximo checkpoint será a integração da decisão estruturada com o fluxo visual existente, sem substituir Draft/Preview/Apply e mantendo o isolamento por tenant.

## Commits relevantes

- `3275de9` — criação da interface `AIProvider`.
- `72ee19f` — Structured Outputs nativos no Claude.
- `66accc2` — SDK Anthropic atual.
- `176d4d1` — configuração segura.
- `4660332` — smoke test MongoDB + Claude.
- `bf90ae8` — teste do parser estruturado.

## Timestamp

2026-09-18
