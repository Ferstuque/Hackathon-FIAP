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
Cada microserviço MUST possuir e gerenciar independentemente seu próprio banco de dados isolado usando PostgreSQL. É expressamente proibido que um servi�o realize leitura ou gravação direta no banco de dados de outro serviço; todo acesso aos dados entre fronteiras deve ocorrer exclusivamente por meio de APIs expostas (síncronas) ou eventos (assíncronos).

### III. IA Driven by Gemini & Pydantic
Toda a camada de an�lise de IA e geração de conte�do MUST utilizar exclusivamente o modelo Gemini 3.1 Pro Preview. A valida��o cont�nua de entrada e sa�da de dados MUST obrigatoriamente fazer uso rigoroso de schemas Pydantic para garantir a conformidade dos contratos da aplicação.

### IV. Security First
A seguran�a � priorit�ria e inegoci�vel no design de cada função. Toda função, API, processamento de evento ou servi�o gerado DEVE possuir forte validação de inputs, aplicar o princ�pio do menor privil�gio e garantir de forma cont�nua que nenhum vazamento de informações sens�veis ocorra.

### V. Observability by Default
A observabilidade é mandatória. Toda operação que altera o estado do sistema, realiza chamadas de rede ou aciona processamentos de IA DEVE emitir traces e logs estruturados com o devido nível de verbosidade. Todos os logs que atravessam chamadas de vários microserviços MUST carregar Ids de rastreamento de correlaçao.

## Stack Constraints

A tecnologia aplicada obedece �s premissas acima e limita o uso a:
- Bancos de Dados: PostgreSQL (isolado por container/servi�o)
- IA e Previs�o Anal�tica: Gemini 3.1 Pro Preview
- Validação Categ�rica e Sanitização: Pydantic

## Quality Gates

As implantações e avaliações arquitet�nicas devem passar por avalia��es regulares para garantir ader�ncia:
- Nenhum microservi�o com acesso a DSN de bancos de dom�nio alheio.
- Falhas em pipelines onde logs exponham senhas devem rejeitar o Build do servi�o.

## Governance

O que est� disposto nesta constitui��o sobrep�e-se a toda documenta��o de arquitetura base, guias de time ou propostas isoladas de frameworks. Altera��es nesta estrutura requerer�o nova emenda constitucional com documenta��o do impacto t�cnico e aprova��o mandat�ria.

**Version**: 1.0.0 | **Ratified**: 2026-05-04 | **Last Amended**: 2026-05-04
