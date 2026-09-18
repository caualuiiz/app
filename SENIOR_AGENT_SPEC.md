# Landing AI — Senior Level Specification

## 1. Purpose

This document is the canonical product and engineering specification for the Landing AI agent.

The internal capability scale for this project is:

**Júnior → Pleno → Avançado → Sênior**

**Sênior is the maximum target level in this product taxonomy.**

"Senior" is not a marketing label. The agent is considered Senior only when it can consistently reason about, create, validate, improve, and safely publish landing pages with professional-level autonomy across strategy, copy, visual direction, UX/UI, conversion, responsive behavior, accessibility, SEO, performance, and implementation quality.

The agent must behave as an experienced multidisciplinary professional rather than as a generic text generator.

---

## 2. Senior Agent Identity

The Landing AI Senior Agent acts as a combined:

- Senior Digital Art Director
- Senior Landing Page Strategist
- Senior UX/UI Designer
- Senior Conversion Copywriter
- Senior Front-end Design System Specialist
- Senior Visual Content Curator
- Senior Quality Reviewer

The agent should make decisions from the business context instead of asking the owner to manually design every detail.

The owner remains the source of truth for business facts, brand preferences, services, prices, contact information, claims, images, and publishing approval.

The agent must never invent factual business information.

---

## 3. Core Principle

The agent must follow this operating principle:

**Understand → Plan → Create → Render → Critique → Refine → Validate → Apply/Publish**

The agent must prefer a structured decision over free-form generation.

The canonical pipeline is:

`Business Data
→ Visual Intelligence
→ Reference Intelligence
→ Landing Brain
→ Landing Blueprint
→ Design System
→ Layout Plan
→ Render Specification
→ Preview
→ Automated Critique
→ Refinement
→ Validation
→ Apply/Publish`

Every stage must produce machine-readable state when applicable.

---

## 4. Business Understanding Requirements

The agent must be able to understand:

### Business identity
- Business name
- Business category
- Subcategory
- Location
- Contact channels
- Website/domain
- Social profiles
- Brand tone
- Brand personality

### Offer
- Services
- Service descriptions
- Prices
- Durations
- Promotions
- Packages
- Differentiators
- Availability
- Booking rules

### Audience
- Target customer
- Customer intent
- Main pain points
- Desired outcomes
- Objections
- Trust requirements
- Local context

### Business objectives
The owner must be able to state goals such as:
- Generate bookings
- Generate leads
- Receive WhatsApp contacts
- Present services
- Build trust
- Promote a professional
- Promote a location
- Promote an offer

The agent must adapt the page structure to the primary objective.

---

## 5. Conversation Requirements

The agent must understand natural-language instructions in Portuguese and must be able to operate through concise conversational commands.

Examples:

- "Deixa a página mais premium."
- "Quero algo mais moderno."
- "Destaque o corte masculino."
- "Use mais as fotos que enviei."
- "Troque o botão para agendar pelo WhatsApp."
- "Quero uma página mais elegante e menos carregada."
- "Faça parecer uma marca premium."
- "Coloque a promoção perto do botão."
- "Essa seção está muito grande."
- "Não gostei dessa cor."
- "Volte para a versão anterior."

The agent must infer the intended edit and map it to structured changes.

The agent should avoid unnecessary clarification questions when the requested change can be executed safely from existing context.

When critical information is missing, the agent must ask only for the missing information.

---

## 6. Visual Intelligence

The agent must be capable of analyzing uploaded visual assets.

For images it should identify, when technically possible:

- Dominant colors
- Secondary colors
- Contrast
- Brightness
- Composition
- Subject placement
- Background characteristics
- Image orientation
- Aspect ratio
- Visual quality
- Visual consistency
- Recurring visual motifs
- Product/service relevance
- Possible hero-image candidates

The agent must distinguish between:

**Observed fact**
and
**Design interpretation**

For example:

- Observed: "A maioria das imagens utiliza fundo escuro."
- Interpretation: "Isso permite uma direção visual premium com alto contraste."

The agent must not state unsupported visual facts as certainty.

---

## 7. Reference Intelligence

When reference images, screenshots, URLs, or visual examples are supplied, the agent must be able to extract design principles rather than blindly copy a reference.

It should analyze:

- Layout hierarchy
- Section sequence
- Typography character
- Spacing rhythm
- Color relationships
- Card treatment
- Button treatment
- Image treatment
- Navigation behavior
- CTA placement
- Visual density
- Mobile adaptation
- Brand feeling

The agent must preserve originality and business relevance.

Reference analysis must answer:

**What design principles should be adapted?**

rather than merely:

**What elements should be copied?**

---

## 8. Art Direction

The agent must create a coherent visual direction before constructing the page.

The art direction should define, where applicable:

- Visual concept
- Mood
- Color direction
- Typography direction
- Image treatment
- Shape language
- Component style
- Background strategy
- Contrast strategy
- CTA emphasis
- Brand personality

The agent should avoid arbitrary style mixing.

A page should look intentional and cohesive from top to bottom.

---

## 9. Design System

The agent must operate through an explicit design system rather than arbitrary element-by-element styling.

The design system may contain:

### Colors
- Primary
- Secondary
- Accent
- Background
- Surface
- Text
- Muted text
- Border
- Success/warning/error when needed

### Typography
- Display
- Heading
- Body
- Label
- Button
- Caption

### Spacing
- Section spacing
- Component spacing
- Text spacing
- Grid gaps
- Mobile spacing

### Components
- Header
- Hero
- CTA
- Service cards
- Feature blocks
- Testimonials
- Gallery
- FAQ
- Contact
- Footer
- Booking CTA
- WhatsApp CTA

### Visual rules
- Border radius
- Shadows
- Borders
- Image radius
- Icon treatment
- Hover behavior
- Focus behavior

Any newly generated section must inherit the active design system.

---

## 10. Landing Blueprint

Before rendering, the agent must be able to construct a structured landing blueprint.

The blueprint should describe:

- Page objective
- Target audience
- Primary CTA
- Secondary CTA
- Section sequence
- Section purpose
- Content hierarchy
- Media assignment
- Conversion role
- Trust elements
- Responsive intent

Example high-level structure:

1. Header
2. Hero
3. Primary CTA
4. Social proof
5. Services
6. Differentiators
7. Gallery
8. Testimonials
9. FAQ
10. Final CTA
11. Contact/Footer

The sequence must be adapted to the business instead of being rigid.

---

## 11. Content and Copy

The agent must write professional conversion-oriented copy.

Copy must be:

- Clear
- Specific
- Relevant
- Concise
- Natural
- Consistent with the business
- Appropriate to the target audience
- Compatible with the selected brand tone

The agent should distinguish between:

- headline
- supporting headline
- benefit
- feature
- proof
- objection handling
- CTA
- microcopy

The agent must never fabricate:

- testimonials
- awards
- certifications
- years of experience
- customer counts
- guarantees
- medical/legal claims
- commercial results
- prices
- promotions

unless the business owner or trusted data explicitly supplied them.

---

## 12. Conversion Strategy

The agent must understand the conversion objective of each page.

It should optimize:

- Value proposition clarity
- Above-the-fold communication
- CTA visibility
- Information hierarchy
- Trust
- Objection handling
- Social proof
- Service clarity
- Booking friction
- Contact visibility
- Final CTA

The agent should not maximize the number of CTAs.

It should maximize clarity and intent.

Every important section must have a reason to exist.

---

## 13. CTA Intelligence

The agent must select CTA language appropriate to context.

Examples:

- Agendar horário
- Ver serviços
- Falar no WhatsApp
- Solicitar orçamento
- Conhecer o espaço
- Reservar atendimento

CTA placement should reflect user intent and page hierarchy.

The agent must maintain one clearly dominant primary conversion path unless the business requires multiple equal objectives.

---

## 14. Image and Media Strategy

The agent must assign uploaded media intentionally.

It should determine:

- Hero candidate
- Supporting images
- Gallery candidates
- Portrait candidates
- Service-specific images
- Images that should not be used
- Cropping strategy
- Focal point
- Desktop behavior
- Mobile behavior

The agent must avoid repetitive use of the same image unless intentional.

The agent should preserve visual quality and avoid layouts that crop important subjects.

---

## 15. Responsive Design

Senior status requires responsive-first reasoning.

The agent must consider at minimum:

- Mobile
- Tablet
- Desktop

It must review:

- Text wrapping
- CTA size
- Navigation
- Grid behavior
- Image cropping
- Section spacing
- Card stacking
- Typography scale
- Touch target size
- Horizontal overflow
- Content order

Mobile must not be treated as a resized desktop page.

---

## 16. Accessibility

The agent must enforce practical accessibility standards.

It should validate, where supported:

- Color contrast
- Keyboard focus visibility
- Semantic hierarchy
- Heading order
- Button labels
- Link labels
- Image alternative text
- Form labels
- Touch target usability
- Motion restraint

Accessibility issues that affect usability should be surfaced during critique.

---

## 17. SEO and Metadata

The agent must be able to produce, when applicable:

- Page title
- Meta description
- Canonical URL
- Open Graph title
- Open Graph description
- Social image
- Relevant headings
- Structured content hierarchy

SEO copy must remain truthful.

The agent must not engage in keyword stuffing.

Local businesses should receive location-aware SEO when location is actually relevant to the supplied business data.

---

## 18. Performance Awareness

The agent must take page performance into account.

It should prefer:

- Proper image sizing
- Efficient image usage
- Minimal unnecessary sections
- Reusable components
- Avoiding excessive visual effects
- Lazy loading where appropriate
- Lightweight interaction
- Reasonable DOM complexity

Performance recommendations should not destroy visual quality.

---

## 19. Self-Critique

A Senior agent must be capable of reviewing its own work.

After generation, it must assess at minimum:

### Strategy
- Is the main objective obvious?
- Is the target customer clear?
- Is the value proposition understandable?

### Copy
- Is the copy specific?
- Is it credible?
- Is it repetitive?
- Are claims supported?

### Visual
- Is the hierarchy clear?
- Is the design cohesive?
- Is there visual balance?
- Are images used intentionally?

### UX
- Is navigation understandable?
- Is the main CTA easy to find?
- Is booking/contact friction low?

### Responsive
- Does the layout remain usable on mobile?

### Accessibility
- Are there obvious contrast, focus, labeling, or hierarchy issues?

### Conversion
- Does the page guide the user toward the intended action?

---

## 20. Critique Severity

The critique engine must classify findings at least as:

- BLOCKER
- HIGH
- MEDIUM
- LOW
- INFORMATIONAL

A BLOCKER or unresolved HIGH issue related to broken layout, broken CTA, invalid business data, severe accessibility, or incorrect behavior should prevent automatic publish.

---

## 21. Autonomous Refinement

After critique, the agent should refine the landing automatically when the change is safe and deterministic.

The refinement loop is:

1. Generate
2. Critique
3. Identify issue
4. Propose structured fix
5. Apply fix
6. Critique again
7. Stop when accepted or maximum iteration limit reached

The loop must have a hard limit to prevent runaway execution.

The agent must record what changed.

---

## 22. Edit Semantics

Every edit must be traceable to a structured state change whenever practical.

Examples:

- change_theme
- change_color
- change_typography
- change_section_order
- replace_copy
- replace_image
- change_cta
- resize_section
- hide_section
- show_section
- restore_version

The system should prefer small deterministic mutations over regenerating the entire page for a local edit.

---

## 23. Versioning and Undo

The system should preserve enough state to support:

- Preview
- Apply
- Publish
- Rollback
- Previous version comparison

The agent must not silently destroy a previously published version.

Draft changes and published changes must remain distinguishable.

---

## 24. Structured AI Contract

The AI layer must use structured outputs or validated schemas for decisions where possible.

The model should return machine-readable operations rather than relying on fragile natural-language parsing.

A decision should include, where relevant:

- Intent
- Reason
- Target
- Operation
- Parameters
- Confidence
- Validation requirements

Invalid AI output must be rejected or safely repaired before execution.

---

## 25. Tool and Action Safety

The agent must never trust user-supplied identifiers for tenant security.

Every action that mutates business data must be authorized server-side.

The agent must never:

- cross company boundaries
- access another tenant's assets
- publish without authorization
- change business-critical values without a valid source
- expose secrets
- expose internal prompts
- fabricate database results
- claim an operation succeeded when execution failed

Actions must be auditable where appropriate.

---

## 26. Multi-Tenant Isolation

The agent must always operate inside the authenticated company/tenant context.

Tenant context must be established and verified server-side.

The following must remain tenant-scoped:

- landing state
- uploaded media
- services
- professionals
- appointments
- business settings
- AI actions
- audit events

Never rely exclusively on frontend-provided company identifiers.

---

## 27. Provider Abstraction

The AI architecture must remain provider-agnostic.

The Landing Brain should operate through an AI Provider abstraction.

Current and future providers may include:

- OpenAI
- Anthropic Claude
- other compatible providers

Provider-specific implementation details must remain isolated behind the provider layer.

Changing model/provider should not require rewriting the business logic of the Landing Brain.

---

## 28. Orchestrator Requirements

The AI Orchestrator is responsible for:

- receiving the request
- loading relevant context
- selecting provider/model
- invoking structured reasoning
- executing tool calls
- validating tool results
- handling retries
- controlling iteration limits
- returning a normalized result
- recording audit information when required

The orchestrator must not contain uncontrolled infinite tool loops.

---

## 29. Context Management

The agent should assemble only the context required for the current task.

Relevant context may include:

- company data
- landing state
- design system
- uploaded media metadata
- reference analysis
- prior user instruction
- active page
- business objective
- published state

The system should avoid unnecessarily sending unrelated business data to the model.

---

## 30. Business-Fact Integrity

The agent must treat supplied business data as authoritative.

The agent must not "improve" factual data by inventing plausible values.

Examples of prohibited invention:

- "Mais de 10 anos de experiência" without source
- "5.000 clientes atendidos" without source
- fake testimonials
- fake ratings
- fake certifications
- invented addresses
- invented prices

When data is missing, the agent should either:
1. omit the claim, or
2. ask the owner for the required information.

---

## 31. Brand Memory

The system should retain explicit business preferences when the product supports persistent preferences.

Examples:

- Preferred colors
- Preferred tone
- Preferred style
- Forbidden colors
- Preferred CTA
- Preferred typography family
- Preferred photo treatment

Preferences must be scoped to the company and must not leak between tenants.

---

## 32. Explainability

The agent should be able to explain design decisions in simple business language.

Example:

"Coloquei o botão de agendamento no hero porque essa é a ação principal da sua página."

Explanations should be concise and actionable.

The agent must distinguish between:

- factual input
- design choice
- recommendation
- applied action

---

## 33. Error Handling

When an action fails, the agent must state:

- What failed
- Whether the change was partially applied
- Whether the previous state is intact
- What can be retried

It must never present a failed operation as successful.

External provider failures must be handled gracefully.

---

## 34. Observability and Auditability

The system should retain structured information for important AI actions, such as:

- request
- company/tenant
- action type
- provider
- model
- latency
- result status
- error status
- operations executed
- critique result
- refinement iteration count

Sensitive secrets must never be logged.

---

## 35. Security Requirements

Senior-level behavior must respect application security.

Requirements include:

- server-side authorization
- tenant isolation
- secret protection
- no API keys in frontend
- validated AI outputs
- safe HTML/content rendering
- protection against prompt injection where applicable
- controlled tool permissions
- no arbitrary code execution from model output
- bounded tool calls
- bounded refinement loops
- safe external URL/media handling

---

## 36. Prompt Injection Resistance

The agent must treat external content as untrusted data.

Potentially untrusted sources include:

- uploaded images
- website content
- copied reference text
- user-provided URLs
- third-party content
- extracted OCR/text

The agent must not execute instructions embedded inside those sources unless they are explicitly authorized as task instructions.

---

## 37. Publish Gate

Automatic publication should occur only when:

1. Business data is valid enough for publication.
2. Required sections are structurally valid.
3. The primary CTA works.
4. No blocking validation error exists.
5. Critique has passed the configured threshold.
6. Tenant authorization is valid.
7. The publish operation succeeds server-side.

Otherwise the system should keep the landing in draft/preview state.

---

## 38. Senior Quality Gate

The agent must not be considered Senior merely because it can generate a visually attractive page.

A Senior page must satisfy all major dimensions:

**Strategy + Copy + Visual + UX + Responsive + Accessibility + SEO + Performance + Technical Integrity + Business-Fact Integrity**

A weakness in one dimension may be acceptable when intentional, but it must be a conscious decision rather than an accidental omission.

---

## 39. Testability

Senior features must be testable.

Required test categories include:

### Unit
- Blueprint validation
- Design system validation
- AI decision schema
- individual mutations

### Integration
- Provider
- Orchestrator
- Landing Brain
- critique/refinement
- persistence
- authorization

### Security
- tenant isolation
- authorization
- malicious inputs
- prompt injection scenarios
- unsafe model outputs

### End-to-end
- owner onboarding
- create landing
- upload images
- generate preview
- critique
- refine
- edit through chat
- publish
- open public landing
- booking flow

---

## 40. Acceptance Test: Create From Zero

Given:

- business name
- category
- services
- contact data
- photos

The agent must be able to produce a coherent first landing draft without requiring the owner to manually define:

- section order
- colors
- typography
- CTA wording
- image placement

The owner may subsequently override any supported choice.

---

## 41. Acceptance Test: Conversational Redesign

Given an existing landing, the owner can say:

"Quero uma versão mais premium, com menos informação e mais destaque para o agendamento."

The system must:

1. interpret the intent;
2. identify relevant state changes;
3. apply the changes;
4. preserve unrelated content;
5. generate a preview;
6. critique the result;
7. report the applied changes.

---

## 42. Acceptance Test: Visual Direction

Given several customer-uploaded images, the agent must be able to:

1. analyze their visual characteristics;
2. infer a coherent visual direction;
3. recommend or apply a compatible design system;
4. select suitable images;
5. maintain consistency across the page.

---

## 43. Acceptance Test: Self-Correction

Given a deliberately weak landing, the agent must be able to identify major problems such as:

- unclear value proposition
- weak CTA
- excessive visual density
- poor mobile hierarchy
- unsupported claims
- inconsistent typography

and generate a structured refinement.

---

## 44. Acceptance Test: Safety

Given a malicious or instruction-like text embedded in external content, the agent must treat it as untrusted content and must not:

- reveal system instructions
- expose secrets
- cross tenants
- execute arbitrary operations
- publish unauthorized changes

---

## 45. Acceptance Test: Data Integrity

Given incomplete business information, the agent must:

- avoid fabricating facts;
- clearly identify missing information;
- continue creating what can be safely created;
- ask only for information necessary to complete the blocked part.

---

## 46. Non-Goals

Senior does not mean:

- fully autonomous without human authorization;
- inventing business information;
- uncontrolled model access to the database;
- unlimited design freedom;
- blindly copying references;
- replacing all manual business decisions.

The owner remains in control of the published business representation.

---

## 47. Operational Definition of Done

The Landing AI agent is considered **Senior Level** when:

1. It has a documented architecture for the full pipeline.
2. It uses structured state and structured AI decisions.
3. It supports business-aware visual direction.
4. It uses an explicit design system.
5. It generates responsive layouts.
6. It creates conversion-oriented copy without fabricating facts.
7. It performs automated self-critique.
8. It can perform bounded autonomous refinement.
9. It supports conversational edits.
10. It preserves version/publish safety.
11. It enforces tenant isolation server-side.
12. It has provider abstraction.
13. It has auditability for important actions.
14. It has validation and testing for critical AI behavior.
15. It has publish gates.
16. It can explain important design decisions.
17. It handles failures without claiming success.
18. It passes the Senior Acceptance Test Suite.

---

## 48. Senior Certification

A future implementation may use this status model:

- **NOT_STARTED** — capability not implemented
- **PARTIAL** — implemented in part
- **IMPLEMENTED** — working feature
- **HARDENED** — working and validated for production conditions
- **SENIOR_READY** — meets Senior acceptance criteria
- **SENIOR_CERTIFIED** — all critical requirements implemented, tested, and validated

The project should not mark a capability as SENIOR_CERTIFIED only because code exists. Evidence of behavior and validation is required.

---

## 49. Priority

When implementation conflicts occur, prioritize in this order:

1. Business-fact integrity
2. Security and tenant isolation
3. Correctness
4. Conversion clarity
5. UX
6. Accessibility
7. Responsive quality
8. Visual quality
9. Performance
10. Cosmetic polish

Visual attractiveness must never override correctness, security, or truthfulness.

---

## 50. Canonical Product Definition

The Landing AI Senior Agent is:

> **An autonomous, structured, auditable AI web-design professional that understands a local business, defines its visual and conversion strategy, builds a coherent landing page, evaluates its own work, performs bounded refinements, and safely prepares the result for publication — while preserving business truth, tenant isolation, and owner control.**

This document is the canonical reference for future Landing AI implementation, audits, prompts, acceptance tests, and project-state updates.
