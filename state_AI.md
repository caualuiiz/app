# AI PROJECT STATE

## Current Phase

Fase 3.2 — Landing Brain: agente profissional de criação de landing pages

## Status

ARQUITETURA CORRIGIDA E IMPLEMENTADA NA BRANCH `feature/ai-phase-3.2`

A direção do projeto foi consolidada: o agente não é um provider externo e não está sendo treinado com dados dos clientes. Ele já possui uma experiência profissional fixa, modelada como um Diretor de Arte Digital e Especialista em Landing Pages com mais de 20 anos de atuação.

## Princípio central

O cliente fornece matéria-prima para análise:
- negócio e objetivo;
- fotos;
- referências;
- serviços e informações fornecidas;
- identidade e contexto do estabelecimento.

O agente já possui o método profissional. Ele analisa esses dados e decide como cada elemento deve ser usado na landing page.

## Implementado

- `professional_brain.py`: identidade, experiência e regras profissionais fixas.
- `reasoning_engine.py`: contrato interno para o motor de raciocínio.
- `landing_brain.py`: executor do agente com persona profissional fixa.
- `AIOrchestrator`: sanitização, preparação do contexto e validação da decisão.
- `StructuredDecision`: contrato estruturado de decisões.
- Validator de campos sensíveis.
- Endpoint autenticado `POST /api/design/ai-decision`.
- Persistência tenant-scoped em `landing_decisions`.
- Configuração `LANDING_BRAIN_MODEL` documentada.
- Removida a dependência Anthropic/Claude da arquitetura desta fase.
- Removidos testes e arquivos específicos do provider Claude.

## Como o agente pensa

1. Entende o negócio e o objetivo comercial.
2. Analisa as evidências visuais.
3. Determina a função de cada foto dentro da página.
4. Define linguagem visual.
5. Harmoniza paleta, tipografia, composição e mídia.
6. Interpreta referências sem copiar.
7. Constrói hierarquia e narrativa.
8. Prioriza clareza, confiança, diferenciação e conversão.
9. Identifica lacunas sem inventar fatos.
10. Faz autocrítica antes de finalizar.

## Regra de experiência

Os dados de cada cliente **não treinam** o agente. Eles são apenas analisados por um profissional que já possui a experiência-base.

## Execução

O modelo de execução é apenas o mecanismo usado para materializar o raciocínio do agente; a identidade, metodologia, critérios, regras e contrato pertencem ao nosso Landing Brain.

## Validação

- Contrato estruturado validado.
- Sanitização de tenant e campos sensíveis validada.
- Testes específicos do Landing Brain adicionados.
- Nenhuma chave externa foi adicionada ao GitHub.

## Próximo passo

A próxima etapa deve transformar as decisões do Landing Brain em decisões visuais concretas dentro do pipeline já existente:

`Landing Brain → Design System → Layout Plan → Render Specification → Preview → Apply`

Depois disso, adicionaremos o ciclo de crítica visual da própria landing antes da publicação.

## Current Pause Point

O conceito central do agente está agora corretamente representado no código: **ele já é experiente; ele não aprende; ele analisa e decide**.

## Timestamp

2026-09-18
