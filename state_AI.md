# AI PROJECT STATE

## Current Phase

Fase 3.4 — Landing Blueprint profissional + compilação para Render Specification

## Status

IMPLEMENTADA NA BRANCH `feature/ai-phase-3.2`; PENDENTE SOMENTE VALIDAÇÃO VISUAL E2E REAL

O conceito do agente está consolidado: ele já possui experiência profissional fixa de 20+ anos. Os dados do cliente são matéria-prima de análise, não treinamento.

## Implementado nesta etapa

- `LandingBlueprint`: contrato completo para identidade, Design System, Layout Plan, posicionamento de mídia, tom e conversão.
- `MediaPlacement`: cada foto pode receber uma função profissional, seções-alvo, prioridade, tratamento, crop e ponto focal.
- `VisualImageInsight`: a análise visual agora pode registrar o papel recomendado de cada imagem.
- `MediaBinding`: Render Specification usa referências seguras como `media.image_01`, ligadas ao arquivo autorizado separadamente.
- Validação de mídia: o Blueprint só aceita imagens presentes no perfil visual autorizado da empresa.
- Validação de seções: referências de mídia só podem apontar para seções existentes no Blueprint.
- `compile_render_spec()`: transforma o Blueprint profissional em uma Render Specification compatível com Preview/Apply.
- Endpoint autenticado `POST /api/design/ai-blueprint`.
- Índice MongoDB para `landing_blueprints`.
- Testes de Blueprint e binding de mídia adicionados.
- Isolamento multi-tenant mantido pela origem autenticada de `company_id`.

## Fluxo atual

`Dados do cliente → Visual Intelligence → Landing Brain → Landing Blueprint → Render Specification → Preview → Apply`

O Landing Brain determina:
- papel de cada foto;
- seção de destino;
- tratamento visual;
- hierarquia;
- identidade visual;
- estrutura;
- estratégia de conversão.

## Regra profissional

O agente não aprende com o cliente. Ele já possui a experiência-base:
**Diretor de Arte Digital + Especialista em Landing Pages, 20+ anos.**

O modelo usado na execução é apenas um mecanismo de materialização do raciocínio; a metodologia e os critérios pertencem ao nosso Landing Brain.

## Segurança

- Contexto enviado ao motor é sanitizado pelo `AIOrchestrator`.
- Identificadores internos, tokens, segredos e credenciais não são enviados.
- Fotos precisam pertencer ao perfil visual da própria empresa.
- Render Specification não expõe diretamente caminhos físicos de mídia nas seções; usa bindings seguros.
- Nenhuma chave externa está versionada no GitHub.

## Testes

- Teste do núcleo profissional do Landing Brain.
- Teste de sanitização.
- Teste do contrato Structured Decision.
- Teste de Blueprint e rejeição de mídia não autorizada.
- Validação estrutural local prevista antes do E2E visual.

## Próximo passo

Executar o primeiro E2E real com uma empresa de teste contendo fotos e referências reais:
1. analisar imagens;
2. gerar Blueprint;
3. compilar Render Specification;
4. criar Preview;
5. verificar visualmente a distribuição das fotos e coerência da identidade;
6. somente depois validar Apply.

Após esse E2E, entraremos no ciclo de **autocrítica visual automática**, no qual o agente recebe o próprio Preview como evidência e propõe correções antes da publicação.

## Current Pause Point

O agente já deixou de ser somente um gerador de decisões e passou a produzir um **Blueprint profissional executável** para a landing.

## Timestamp

2026-09-18
