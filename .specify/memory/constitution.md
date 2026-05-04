<!-- SYNC IMPACT REPORT
Version change: 0.0.0 -> 1.0.0
Modified principles:
  - [PRINCIPLE_1_NAME] -> I. Microservices & Clean Architecture
  - [PRINCIPLE_2_NAME] -> II. Database per Service
  - [PRINCIPLE_3_NAME] -> III. IA Driven by Gemini & Pydantic
  - [PRINCIPLE_4_NAME] -> IV. Security First
  - [PRINCIPLE_5_NAME] -> V. Observability by Default
Added sections: Stack Constraints, Quality Gates
Removed sections: None
Templates requiring updates:
  - [ ] .specify/templates/plan-template.md - Needs Microservices and security checks alignment
  - [ ] .specify/templates/spec-template.md - Needs DB per service limits confirmation
Follow-up TODOs: None.
-->

# Hackathon FIAP Constitution

## Core Principles

### I. Microservices & Clean Architecture
O sistema MUST ser desenvolvido utilizando arquitetura de microserviços, seguindo rigorosamente as práticas de Clean Architecture. Os limites entre as camadas (Domain, Use Cases, Interfaces/Adapters, Infrastructure) devem ser protegidos e restritos em cada serviço, promovendo baixo acoplamento e alta coesão.

### II. Database per Service
Cada microserviço MUST possuir e gerenciar independentemente seu próprio banco de dados isolado usando PostgreSQL. É expressamente proibido que um serviço realize leitura ou gravação direta no banco de dados de outro serviço; todo acesso aos dados entre fronteiras deve ocorrer exclusivamente por meio de APIs expostas (síncronas) ou eventos (assíncronos).

### III. IA Driven by Gemini & Pydantic
Toda a camada de análise de IA e geração de conteúdo MUST utilizar exclusivamente o modelo Gemini 3.1 Pro Preview. A validação contínua de entrada e saída de dados MUST obrigatoriamente fazer uso rigoroso de schemas Pydantic para garantir a conformidade dos contratos da aplicação.

### IV. Security First
A segurança é prioritária e inegociável no design de cada função. Toda função, API, processamento de evento ou serviço gerado DEVE possuir forte validação de inputs, aplicar o princípio do menor privilégio e garantir de forma contínua que nenhum vazamento de informações sensíveis ocorra.

### V. Observability by Default
A observabilidade é mandatória. Toda operação que altera o estado do sistema, realiza chamadas de rede ou aciona processamentos de IA DEVE emitir traces e logs estruturados com o devido nível de verbosidade. Todos os logs que atravessam chamadas de vários microserviços MUST carregar Ids de rastreamento de correlação.

## Stack Constraints

A tecnologia aplicada obedece às premissas acima e limita o uso a:
- Bancos de Dados: PostgreSQL (isolado por container/serviço)
- IA e Previsão Analítica: Gemini 3.1 Pro Preview
- Validação Categórica e Sanitização: Pydantic

## Quality Gates

As implantações e avaliações arquitetônicas devem passar por avaliações regulares para garantir aderência:
- Nenhum microserviço com acesso a DSN de bancos de domínio alheio.
- Falhas em pipelines onde logs exponham senhas devem rejeitar o Build do serviço.

## Governance

O que está disposto nesta constituição sobrepõe-se a toda documentação de arquitetura base, guias de time ou propostas isoladas de frameworks. Alterações nesta estrutura requererão nova emenda constitucional com documentação do impacto técnico e aprovação mandatória.

**Version**: 1.0.0 | **Ratified**: 2026-05-04 | **Last Amended**: 2026-05-04
